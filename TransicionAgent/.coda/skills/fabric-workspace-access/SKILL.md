---
name: fabric-workspace-access
description: Consulta ROLES DE USUARIOS y CAPACIDAD de un workspace de Microsoft Fabric vía API REST (roleAssignments, workspaces, capacities) para documentar el TRS-9 - sección 1 (Ambientes) y roles asignados. Devuelve Admin/Member/Contributor/Viewer con sus UPN/appIds, y sku/región/estado de la capacidad. Usar cuando el usuario pida roles de workspace, usuarios asignados, capacidad, SKU o licenciamiento de un workspace de Fabric, y el MCP de Fabric no exponga esos datos.
---

# Roles y capacidad de un workspace de Fabric vía API REST

Esta skill complementa al MCP de Fabric para llenar la sección 1 del TRS-9
(roles asignados al workspace) y datos de capacidad/licenciamiento. Todo en
modo solo lectura.

## Cuándo usar esta skill

- El usuario pide los roles asignados de un workspace de Fabric (Admin,
  Member, Contributor, Viewer) y quiénes los tienen.
- El usuario pide la capacidad del workspace (ID, SKU, región, estado).
- El MCP de Fabric no expone roleAssignments ni capacities.

## Requisitos previos

1. **`az login` activo** (el script usa `AzureCliCredential`).
2. Dependencias: `azure-identity` y `requests` (ya disponibles con `uv sync`).
3. **Permisos**: rol **Member o superior en el workspace** (no exige Admin del
   workspace ni Fabric Admin). Scope `Workspace.Read.All`. SPN soportado.

## Archivos incluidos

- `scripts/fabric_rest_client.py` — cliente REST compartido (en
  `.coda/skills/fabric-rest-api/scripts/`).
- `scripts/consultar_acceso_workspace.py` — script principal de esta skill.

## Cómo usar esta skill

### 1. Ejecutar la consulta

```bash
# Roles + capacidad del workspace
uv run python consultar_acceso_workspace.py --workspace <workspaceId>

# Solo roles
uv run python consultar_acceso_workspace.py --workspace <ws> --solo-roles

# Guardar roles como CSV
uv run python consultar_acceso_workspace.py --workspace <ws> --output roles.csv
```

### 2. Qué devuelve

- **Roles**: tabla con rol (`Admin`, `Member`, `Contributor`, `Viewer`),
  nombre del principal y su identificador:
  - User → `userDetails.userPrincipalName` (UPN)
  - ServicePrincipal → `servicePrincipalDetails.aadAppId`
  - Group → tipo de grupo (los miembros del grupo NO se expanden; para
    listarlos usar Graph API o el portal)
- **Capacidad**: `capacityId` del workspace (`GET /v1/workspaces/{w}`) y, si
  el usuario es admin/contributor de la capacidad, `sku`, `region` y `state`
  (`GET /v1/capacities`, scope `Capacity.Read.All`, 50/min).

### 3. Limitaciones importantes (comunicar siempre al usuario)

- **Grupos**: aparecen como un solo principal sin expandir miembros.
- **Si el caller es solo Viewer** del workspace: el endpoint devuelve 403;
  se necesita Member o superior. El script muestra ese mensaje claramente.
- **Alternativa admin**: `GET /v1/admin/workspaces/{w}/users` (Preview,
  200 req/hora) requiere rol Fabric Admin; usar solo como complemento.
- **Líder funcional / responsable del dominio**: son datos organizacionales
  que no están en Fabric; pedirlos al usuario.
