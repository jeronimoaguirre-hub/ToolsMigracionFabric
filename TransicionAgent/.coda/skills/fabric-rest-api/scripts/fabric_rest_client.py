"""
Cliente REST de solo lectura para la API de Microsoft Fabric
(https://api.fabric.microsoft.com/v1) y la API heredada de Power BI
(https://api.powerbi.com/v1.0/myorg).

Por qué existe: el MCP de Fabric (Microsoft.Fabric.Mcp) no expone conexiones,
gateways, schedules de pipelines, historial de runs ni roles de workspace.
La API REST de Fabric sí lo hace, y este módulo la consume en modo lectura.

Autenticación: AzureCliCredential (requiere `az login` activo). El token se
obtiene con scope `.default` del recurso y azure-identity lo cachea y renueva
en memoria; no se persisten tokens en disco.

Modo lectura: whitelist de métodos GET. Las únicas excepciones son los POST
de lectura en la práctica (`gateways/{id}/checkStatus` y
`datapipelines/.../queryactivityruns`). Todo PUT/PATCH/DELETE y el resto de
POST están bloqueados a propósito.

Uso típico desde otro script:

    from fabric_rest_client import FabricRestClient
    client = FabricRestClient()
    conns = client.get_all("/connections")
    gw = client.get(f"/gateways/{gateway_id}")
    client.check_gateway_status(gateway_id)   # POST de lectura, con LRO
"""

import time
from typing import Any, Dict, Iterator, List, Optional

import requests
from azure.identity import AzureCliCredential

FABRIC_BASE = "https://api.fabric.microsoft.com/v1"
FABRIC_SCOPE = "https://api.fabric.microsoft.com/.default"
POWERBI_BASE = "https://api.powerbi.com/v1.0/myorg"
POWERBI_SCOPE = "https://analysis.windows.net/powerbi/api/.default"

# POST permitidos: son operaciones de lectura (status / query), no mutan datos.
_ALLOWED_POST_SUFFIXES = (
    "/checkStatus",
    "/queryactivityruns",
)

DEFAULT_TIMEOUT = 60


class FabricRestError(RuntimeError):
    """Error al llamar la API de Fabric/Power BI."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class FabricRestClient:
    """Cliente HTTP de solo lectura para Fabric y Power BI REST APIs."""

    def __init__(self, use_powerbi: bool = False):
        self.base_url = POWERBI_BASE if use_powerbi else FABRIC_BASE
        self.scope = POWERBI_SCOPE if use_powerbi else FABRIC_SCOPE
        # process_timeout=60: el default (10 s) es insuficiente cuando `az`
        # tarda ~8 s en emitir el token y falla de forma intermitente con
        # CredentialUnavailableError: Failed to invoke the Azure CLI.
        self._credential = AzureCliCredential(process_timeout=60)
        self._session = requests.Session()
        self._token_cache: Dict[str, Any] = {}

    # ------------------------------------------------------------------ #
    # Token / headers
    # ------------------------------------------------------------------ #

    def get_token(self, scope: Optional[str] = None) -> str:
        """Token con caché en memoria (renueva 5 min antes de expirar).

        AzureCliCredential NO cachea: cada get_token() lanza `az` (~8 s). Sin
        este caché, cada request HTTP costaba ~8 s y los barridos tardaban
        minutos o fallaban por timeout.
        """
        scope = scope or self.scope
        cached = self._token_cache.get(scope)
        if cached and cached.expires_on - time.time() > 300:
            return cached.token
        token = self._credential.get_token(scope)
        self._token_cache[scope] = token
        return token.token

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.get_token()}"}

    # ------------------------------------------------------------------ #
    # HTTP core
    # @staticmethod
    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> requests.Response:
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        method_upper = method.upper()

        # Guardarraíl de solo lectura.
        if method_upper not in ("GET", "POST"):
            raise FabricRestError(
                f"Método {method_upper} bloqueado: esta skill opera en modo "
                "solo lectura (solo GET, más checkStatus y queryactivityruns)."
            )
        if method_upper == "POST" and not any(
            url.rstrip("/").endswith(suffix) for suffix in _ALLOWED_POST_SUFFIXES
        ):
            raise FabricRestError(
                f"POST bloqueado (solo se permiten {', '.join(_ALLOWED_POST_SUFFIXES)}): {url}"
            )

        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            response = self._session.request(
                method_upper,
                url,
                headers=self._headers(),
                params=params,
                json=json_body,
                timeout=timeout,
            )
            if response.status_code == 429 and attempt < max_attempts:
                retry_after = int(response.headers.get("Retry-After", 5))
                time.sleep(retry_after)
                continue
            return response
        return response

    # ------------------------------------------------------------------ #
    # GET simple
    # ------------------------------------------------------------------ #

    def get(self, path: str, **params: Any) -> Dict[str, Any]:
        """GET que devuelve el JSON completo de la respuesta."""
        response = self._request("GET", path, params=params or None)
        if response.status_code != 200:
            raise FabricRestError(
                f"GET {path} -> HTTP {response.status_code}: {response.text[:500]}",
                status_code=response.status_code,
            )
        return response.json()

    def get_raw(self, path: str, **params: Any) -> requests.Response:
        """GET que devuelve el objeto Response (para LRO / 202)."""
        return self._request("GET", path, params=params or None)

    # ------------------------------------------------------------------ #
    # GET paginado
    # ------------------------------------------------------------------ #

    def get_all(self, path: str, **params: Any) -> list:
        """GET con paginación automática por continuationUri/continuationToken.

        Devuelve la lista acumulada de `value` de todas las páginas.
        """
        items: list = []
        url: Optional[str] = (
            path if path.startswith("http") else f"{self.base_url}{path}"
        )
        first_params: Optional[Dict[str, Any]] = params or None
        while url:
            response = self._request("GET", url, params=first_params)
            if response.status_code != 200:
                raise FabricRestError(
                    f"GET {path} -> HTTP {response.status_code}: {response.text[:500]}",
                    status_code=response.status_code,
                )
            payload = response.json()
            values = payload.get("value", [])
            if isinstance(values, list):
                items.extend(values)
            continuation_uri = payload.get("continuationUri")
            if continuation_uri:
                url = continuation_uri
                first_params = None  # el continuationUri ya trae los params
            else:
                url = None
        return items

    # ------------------------------------------------------------------ #
    # POST de lectura permitidos
    # ------------------------------------------------------------------ #

    def check_gateway_status(self, gateway_id: str) -> Dict[str, Any]:
        """POST /gateways/{id}/checkStatus (operación larga, 202 + espera).

        Devuelve dict con status (Online/Offline), gatewayVersion,
        gatewayUpgradeState y errorDetails.
        """
        url = f"{self.base_url}/gateways/{gateway_id}/checkStatus"
        response = self._request("POST", url)
        if response.status_code == 200:
            return response.json() if response.text else {}
        if response.status_code not in (200, 202):
            raise FabricRestError(
                f"checkStatus {gateway_id} -> HTTP {response.status_code}: "
                f"{response.text[:500]}",
                status_code=response.status_code,
            )
        # LRO: 202 con Location/Retry-After; sondear hasta que dé resultado.
        poll_url = response.headers.get("Location") or response.headers.get(
            "Operation-Location"
        )
        retry_after = int(response.headers.get("Retry-After", 5))
        deadline = time.time() + 120
        while time.time() < deadline:
            time.sleep(retry_after)
            if poll_url:
                poll = self._session.get(poll_url, headers=self._headers(), timeout=60)
                if poll.status_code == 200:
                    return poll.json() if poll.text else {}
                retry_after = int(poll.headers.get("Retry-After", retry_after))
            else:
                retry = self._request("POST", url)
                if retry.status_code == 200:
                    return retry.json() if retry.text else {}
        raise FabricRestError(
            f"checkStatus del gateway {gateway_id} no terminó a tiempo (LRO)."
        )

    def query_activity_runs(
        self,
        workspace_id: str,
        pipeline_id: str,
        job_instance_id: str,
        last_updated_after: str,
        last_updated_before: str,
    ) -> Dict[str, Any]:
        """POST queryactivityruns: detalle por actividad de un run de pipeline."""
        path = (
            f"/workspaces/{workspace_id}/datapipelines/pipelineruns/"
            f"{job_instance_id}/queryactivityruns"
        )
        body = {
            "lastUpdatedAfter": last_updated_after,
            "lastUpdatedBefore": last_updated_before,
            "orderBy": [{"orderBy": "ActivityRunStart", "order": "ASC"}],
        }
        response = self._request("POST", f"{self.base_url}{path}", json_body=body)
        if response.status_code != 200:
            raise FabricRestError(
                f"queryactivityruns -> HTTP {response.status_code}: {response.text[:500]}",
                status_code=response.status_code,
            )
        return response.json()
