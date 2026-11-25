---
name: fabric-connections-audit
description: Audita las CONEXIONES de Microsoft Fabric vía API REST (https://api.fabric.microsoft.com/v1) para documentar el TRS-9 - secciones 2 (Fuentes de Datos y Conexiones) y 7 (Inventario). Devuelve displayName, connectivityType, credentialType, gateway, recencia de uso de credencial y estado del gateway (Online/Offline). Usar cuando el usuario pida documentar/auditar conexiones, credenciales, gateways, método de autenticación o vencimiento de credenciales de Fabric, y el MCP de Fabric no exponga esos datos.
---

# Auditoría de conexiones de Fabric vía API REST

Esta skill complementa al MCP de Fabric para llenar las secciones 2 y 7 del
TRS-9: conexiones, tipo de credencial, gateways y su estado. Todo en modo
solo lectura.

## Cuándo usar esta skill

- El usuario pide documentar/auditar las conexiones de un workspace o
  pipeline de Fabric (sección 2 del TRS-9).
- El usuario pregunta por gateway, método de autenticación o vencimiento de
  credenciales de conexiones de Fabric.
- El MCP de Fabric no expone esos datos y se necesita la API REST.

## Requisitos previos

1. **`az login` activo** — el script usa `AzureCliCredential`. Si falla con
   `AzureCliCredential` pide al usuario ejecutar `az login` (tenant ECP).
2. Dependencias: `azure-identity` y `requests` (ya disponibles con `uv sync`).
3. **Permisos**: `GET /v1/connections` solo devuelve las conexiones sobre las
   que el usuario tiene permiso. Para un inventario global se necesita rol
   Fabric Admin (`/v1/admin/connections`, Preview, 10 req/min).

## Para el TRS-9: conexiones realmente usadas por un workspace

```bash
uv run python .coda/skills/fabric-connections-audit/scripts/conexiones_workspace.py   --workspace "<WS Silver>" --workspace "<WS Gold>" --con-gateways   --output .coda/tmp/conexiones-usadas.json
```
Recorre los pipelines, toma las conexiones que cada uno usa y las cruza con
`/connections` y `/gateways`: devuelve nombre, conectividad, tipo de credencial,
tipo+path (host/BD), gateway y estado, y qué pipelines la usan. Es lo que debe
alimentar la sección "Fuentes de Datos y Conexiones". `auditar_conexiones.py`
(abajo) lista TODAS las conexiones visibles del tenant: úsalo solo para auditorías
generales. Un gateway que no sale en `GET /gateways` no es visible para el usuario.

## Archivos incluidos

- `scripts/fabric_rest_client.py` — cliente REST compartido (en
  `.coda/skills/fabric-rest-api/scripts/`).
- `scripts/auditar_conexiones.py` — script principal de esta skill.

## Cómo usar esta skill

### 1. Ejecutar la auditoría

```bash
# Todas las conexiones visibles por el usuario
uv run python auditar_conexiones.py

# Filtrar por texto en el nombre (ej. un dominio o producto)
uv run python auditar_conexiones.py --filtro "Ventas"

# Incluir estado de gateways (POST checkStatus, puede tardar; máx 10/min)
uv run python auditar_conexiones.py --con-gateways

# Guardar el resultado como CSV
uv run python auditar_conexiones.py --output conexiones.csv
```

### 2. Qué devuelve

Una tabla con: nombre de la conexión, tipo de conectividad
(`ShareableCloud`, `OnPremisesGateway`, `VirtualNetworkGateway`, ...), tipo de
credencial (`Basic`, `OAuth2`, `ServicePrincipal`, `Key`, `Windows`, ...),
gateway asociado (ID y estado Online/Offline si se pidió `--con-gateways`),
y fechas de recencia (`lastCredentialUsedDateTime`, `lastBoundDateTime`).

### 3. Cruce con pipelines (opcional)

Para saber qué conexiones usa cada pipeline: `GET
/v1/workspaces/{workspaceId}/items/{itemId}/connections` (requiere
`Item.ReadWrite.All` y permiso de escritura sobre el ítem). Ese endpoint solo
trae `id, displayName, connectivityType, connectionDetails, gatewayId`; para
el `credentialType` hay que cruzar por `id` contra el listado de `/connections`.

### 4. Limitaciones importantes (comunicar siempre al usuario)

- **Vencimiento de credenciales: NO disponible por API.** Ningún endpoint
  devuelve fecha de vencimiento ni estado de validez. Verificar en el portal
  de Fabric (Manage connections and gateways). Señales indirectas: el rol
  `PendingOwner` en la conexión indica que la credencial debe renovarse, y
  `connectionRecency.lastCredentialUsedDateTime` muestra el último uso.
- **Secretos/passwords: nunca se exponen** (solo el tipo de credencial).
- **Estado de conexiones cloud: no existe**; solo gateways tienen
  `checkStatus`.
- Throttling: 50 llamadas/min en `/connections`; ante 429 el cliente reintenta
  con `Retry-After`.
