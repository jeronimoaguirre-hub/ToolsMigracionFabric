# TransicionAgent

Herramienta agéntica (para **CODA**) que genera la documentación de transición **TRS - 9**
de un producto de datos en Microsoft Fabric:

- `Inventario_Fabric_<Producto>.xlsx` — inventario de objetos (items, carpetas, tablas,
  pipelines con frecuencia y duración promedio) de los workspaces Silver/Gold.
- Página **padre** TRS - 9 (ambientes y capacitaciones) y página **hija** por release
  (ambientes, conexiones, archivos, modelo, arquitectura, pipelines, inventario, capacitación).
- Publicación en la wiki de Azure DevOps, **solo con tu confirmación**.

Todo se obtiene con datos reales de Fabric en **modo solo lectura**; lo que no se puede
obtener por API (líder funcional, vencimiento de credenciales, capacitaciones...) queda
marcado como `<DATO REQUERIDO: ...>` para que lo completes.

## Cómo usarlo

1. Clona (o copia) esta carpeta en tu entorno de trabajo y ábrela con CODA.
2. Ten a mano: acceso a los workspaces en Fabric (idealmente rol Member+ para ver roles),
   `az login` hecho y VPN si aplica.
3. Pídele a CODA, por ejemplo: *"Haz la documentación de transición TRS - 9 del producto X"*.
   CODA seguirá `TRS - 9/instruction.md`: verificará e instalará dependencias, te hará las
   preguntas necesarias (workspaces, release, destino en la wiki, responsables...), generará
   los archivos y te presentará el plan de publicación para que lo apruebes.

### Requisitos del equipo (CODA te indica lo que falte)

| Requisito | Para qué | Instalación |
|---|---|---|
| Python 3.13 y [uv](https://docs.astral.sh/uv/) | Dependencias y scripts | `pip install uv` |
| Azure CLI + `az login` | Autenticación contra Fabric | https://aka.ms/installazurecli |
| `fab` ([Fabric CLI](https://microsoft.github.io/fabric-cli/)) | Explorar workspaces | lo instala el preflight (`uv tool install ms-fabric-cli`) |
| Node.js LTS | MCP de Azure DevOps (publicación) | https://nodejs.org |
| .NET 10 SDK (`dnx`) | MCP de Fabric | https://dotnet.microsoft.com |
| ODBC Driver 18 for SQL Server | Solo si hay que consultar SQL (Warehouse Gold) | https://aka.ms/odbc18 |

Verificación manual: `python .coda/skills/trs9-preflight/scripts/preflight.py [--instalar]`.

## Estructura

Ver `AGENTS.md` (mapa del repo y reglas) y `TRS - 9/instruction.md` (flujo completo).
Las salidas generadas y `.coda/tmp/` no se versionan.

## Actualizaciones de la plantilla

No edites `.coda/` ni `TRS - 9/*.template.*` en tu copia; si algo del harness no te sirve,
propón el cambio en el repo de la plantilla.
