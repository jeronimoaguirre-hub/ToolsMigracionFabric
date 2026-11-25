"""
Autenticación a Microsoft Fabric (Entra ID) con caché de token persistente en
disco, para no tener que hacer login interactivo en cada conexión ni en cada
ejecución del script.

Por qué existe esto: `Authentication=ActiveDirectoryInteractive` del driver
ODBC de SQL Server abre un login de navegador CADA VEZ que se abre una
conexión nueva (no reutiliza el token entre procesos ni siempre entre
conexiones del mismo proceso). Para un barrido de decenas/cientos de
consultas eso es inviable. Esto hace lo mismo pero con MSAL manejando el
caché explícitamente:

    1. Primera vez: abre el navegador una sola vez (login interactivo).
    2. Guarda el token (y el refresh token) cifrado por el propio MSAL en
       un archivo local (`.fabric_msal_cache.bin`, junto a este script).
    3. Siguientes conexiones -incluso en procesos/ejecuciones nuevas-
       reutilizan el token en silencio (acquire_token_silent) mientras el
       refresh token siga vigente (normalmente varias semanas), sin volver
       a pedir login.
    4. El token se pasa directo a pyodbc vía SQL_COPT_SS_ACCESS_TOKEN, sin
       necesidad de que el DRIVER haga el flujo de Authentication=...

El archivo de caché contiene un token de sesión -no una contraseña-, pero
igual es información sensible: no se debe compartir ni subir a control de
versiones.

Client ID usado: el de Azure CLI (04b07795-8ddb-461a-bbee-02f9e1bf7b46),
una aplicación pública de Microsoft ya registrada y consentida en la
mayoría de tenants de Entra ID para el recurso https://database.windows.net
(SQL/Fabric) — no requiere registrar una app propia en Entra ID.
"""

import struct
from pathlib import Path

import msal

CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"  # Azure CLI (público, pre-consentido)
AUTHORITY = "https://login.microsoftonline.com/organizations"
SCOPE = ["https://database.windows.net/.default"]

CACHE_PATH = Path(__file__).parent / ".fabric_msal_cache.bin"

SQL_COPT_SS_ACCESS_TOKEN = 1256


def _cargar_cache() -> msal.SerializableTokenCache:
    cache = msal.SerializableTokenCache()
    if CACHE_PATH.exists():
        cache.deserialize(CACHE_PATH.read_text(encoding="utf-8"))
    return cache


def _guardar_cache(cache: msal.SerializableTokenCache) -> None:
    if cache.has_state_changed:
        CACHE_PATH.write_text(cache.serialize(), encoding="utf-8")


def obtener_access_token() -> str:
    """Devuelve un access token válido para Fabric/SQL, reutilizando el
    caché en disco si es posible y pidiendo login interactivo solo si hace
    falta (primera vez, o si el refresh token ya expiró)."""
    cache = _cargar_cache()
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)

    resultado = None
    cuentas = app.get_accounts()
    if cuentas:
        resultado = app.acquire_token_silent(SCOPE, account=cuentas[0])

    if not resultado:
        print("No hay token cacheado (o expiró): se abrirá el navegador para login (una sola vez).")
        resultado = app.acquire_token_interactive(scopes=SCOPE)

    _guardar_cache(app.token_cache)

    if "access_token" not in resultado:
        raise RuntimeError(
            f"No se pudo obtener el access token de Entra ID: "
            f"{resultado.get('error')}: {resultado.get('error_description')}"
        )
    return resultado["access_token"]


def token_a_attrs_before(token: str) -> dict:
    """Empaqueta el access token en el formato binario que pyodbc/ODBC
    espera para SQL_COPT_SS_ACCESS_TOKEN (ver docs de Microsoft: struct
    de 4 bytes de longitud + el token en UTF-16-LE)."""
    token_bytes = token.encode("utf-16-le")
    token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
    return {SQL_COPT_SS_ACCESS_TOKEN: token_struct}


def limpiar_cache() -> None:
    """Utilidad de diagnóstico: borra el caché para forzar un login nuevo."""
    if CACHE_PATH.exists():
        CACHE_PATH.unlink()
        print(f"Caché borrado: {CACHE_PATH}")
    else:
        print("No había caché que borrar.")


if __name__ == "__main__":
    token = obtener_access_token()
    print(f"Token obtenido correctamente (longitud: {len(token)} caracteres).")
    print(f"Caché guardado en: {CACHE_PATH}")
