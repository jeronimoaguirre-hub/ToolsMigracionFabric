# TransicionAgent — Documentación de transición TRS - 9 (Microsoft Fabric)

Este repo es una **plantilla**: cada producto de datos usa su propia copia. Sirve para
generar, con datos reales de Fabric, la documentación de transición a producción
(Inventario Fabric `.xlsx` + páginas TRS - 9 padre e hija) y publicarla en la wiki de
Azure DevOps **solo con permiso explícito del usuario**.

## Cuándo se activa

Cuando el usuario pida **documentación de transición, TRS - 9, apropiación técnica,
inventario de Fabric** o "pasar un producto de datos a producción":

1. **Lee completo `TRS - 9/instruction.md`** y sigue sus fases en orden. Es la única fuente
   del flujo; no improvises pasos ni inventes datos.
2. Empieza por el preflight (Fase 1):
   `python .coda/skills/trs9-preflight/scripts/preflight.py` (con `--instalar` para
   instalar dependencias Python y `fab`, previa confirmación del usuario).
3. Haz las preguntas de la Fase 2 (workspace Silver y lakehouse, Gold si aplica, release,
   ambiente, destino en la wiki, datos organizacionales) en **una sola ronda**.
4. Recolecta, llena las plantillas y presenta el **plan de publicación**; publica solo
   después de que el usuario lo confirme (Fase 6).

## Mapa del repo

| Ruta | Qué es |
|---|---|
| `TRS - 9/instruction.md` | Flujo completo que debe seguir el agente |
| `TRS - 9/*.template.*` | Plantillas (no se modifican; se copian y llenan) |
| `.coda/skills/` | Skills: `trs9-preflight`, `fabric-inventory`, `fabric-connections-audit`, `fabric-pipeline-ops`, `fabric-workspace-access`, `fabric-odbc-query`, `fabric-rest-api` (cliente común) |
| `.coda/mcp.json` | MCP de Fabric y de Azure DevOps |
| `.coda/config.json` | Permisos: qué comandos corren sin preguntar y qué está denegado |
| `.coda/tmp/` | Temporales de la corrida (no se versionan) |
| Raíz | Salidas generadas: `Inventario_Fabric_<Producto>.xlsx`, `TRS-9 Padre - <Producto>.md`, `TRS-9 Hija (Release NN) - <Producto>.md` (no se versionan) |

## Reglas que nunca se rompen

- **Solo lectura sobre Fabric.** Nunca crear/modificar/borrar items, conexiones ni roles.
- **No inventar datos:** lo que no se pueda obtener queda como `<DATO REQUERIDO: ...>`.
- **Nunca leer ni mostrar `.env`, tokens o contraseñas.**
- **No publicar en la wiki sin confirmación explícita** del usuario (ruta, crear/actualizar, contenido).
- El **Modelo de Datos** no se llena en la transición (se diligencia desde el inicio del producto).
- Para dependencias: `uv` (`uv sync`, `uv run python ...`).
