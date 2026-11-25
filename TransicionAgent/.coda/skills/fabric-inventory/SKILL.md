---
name: fabric-inventory
description: Recolecta en UNA sola corrida (solo lectura) el inventario completo de uno o más workspaces de Microsoft Fabric — items, ruta de carpetas, tablas Delta por esquema, schedules y duración promedio de pipelines — y llena la plantilla Inventario_Fabric_WS_XXX.xlsx del TRS-9. Usar siempre que haya que llenar el Inventario Fabric o necesitar la lista de objetos/pipelines/tablas de un workspace; evita escribir decenas de scripts ad-hoc.
---

# Inventario de workspaces de Fabric (recolectar + llenar xlsx)

Dos scripts encadenados. **Úsalos en lugar de improvisar `python -c`**: lo que
antes tomaba decenas de llamadas y más de 40 minutos se hace en ~1 minuto.

## Requisitos
- `az login` activo (tenant Ecopetrol). Dependencias: `azure-identity`,
  `requests`, `openpyxl` (ver `instruction.md`, Fase 3).
- Permiso de lectura sobre cada workspace. Para tablas vía OneLake se necesita
  rol de workspace con acceso a los datos (si OneLake devuelve 403 en un
  workspace, queda un aviso en el JSON y esas tablas no se listan).

## Paso 1 — Recolectar
```bash
uv run python .coda/skills/fabric-inventory/scripts/recolectar_workspace.py \
  --workspace "Silver=<nombre o GUID del workspace Silver>" \
  --workspace "Gold=<nombre o GUID del workspace Gold>" \
  --output .coda/tmp/inventario-datos.json
```
- `Capa=` (Bronze|Silver|Gold) es la capa por defecto del workspace; cada item
  la sobrescribe si su nombre tiene prefijo `brz`/`slv`/`gld` (ej. `lh_brz_*`
  dentro de un workspace Silver queda como Bronze).
- Si un nombre no existe exacto, el script **no adivina**: lista los parecidos y
  sale con código 2. Confirma con el usuario cuál es y repite.
- Opciones: `--sin-tablas`, `--sin-pipelines`.
- Qué NO cubre: tablas/vistas de un **Warehouse** (el JSON trae un aviso) → usar
  `fabric-odbc-query` con `INFORMATION_SCHEMA`; roles → `fabric-workspace-access`;
  conexiones → `fabric-connections-audit`.

## Paso 2 — (opcional) Redactar descripciones faltantes
Los items sin descripción en Fabric salen como `<DATO REQUERIDO: DESCRIPCION>`.
Si puedes redactar una descripción **fiel** (leyendo la definición del
notebook/pipeline o por el nombre cuando es evidente), guárdalas en un JSON
`{"nombre_objeto": "descripción"}` y pásalo con `--descripciones`. No inventes:
si no sabes qué hace, déjalo pendiente.

## Paso 3 — Llenar el xlsx
```bash
uv run python .coda/skills/fabric-inventory/scripts/llenar_inventario.py \
  --datos .coda/tmp/inventario-datos.json \
  --salida Inventario_Fabric_<Producto>.xlsx \
  --nombre-workspace "<WS Silver> / <WS Gold>" \
  --ambiente DEV/QA --estado Nuevo \
  [--responsable "<Responsable del dominio>"] [--descripciones .coda/tmp/descripciones.json]
```
El script valida los encabezados de la plantilla, escribe 11 columnas
alineadas, conserva estilos, relee el archivo y reporta filas, conteo por tipo y
celdas pendientes.

## Notas de mapeo
- Carpeta: ruta real del item en Fabric. Última carpeta → *Subcarpeta*; el resto
  → *Nombre de Carpeta*. Raíz → `(raíz)` / `-`.
- Tablas Delta: carpeta `<lakehouse>/Tables`, subcarpeta = esquema.
- Pipelines: frecuencia = schedules (`ACTIVO`/`deshabilitado`) o `Sin schedule (manual)`;
  duración = promedio de ~100 runs recientes, `Sin ejecuciones` si no hay.
- Las dos columnas de duración repiten el mismo valor (la plantilla duplica el
  encabezado "(QA)"); menciónalo en el reporte final.
