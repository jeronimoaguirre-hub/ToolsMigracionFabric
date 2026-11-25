---
name: fabric-pipeline-ops
description: Consulta SCHEDULES e HISTORIAL DE EJECUCIONES de pipelines de Microsoft Fabric vía API REST (Job Scheduler) para documentar el TRS-9 - sección 6 (Pipelines Históricos e Incrementales) - frecuencia de ejecución, duración promedio, tasa de fallo y último error. Usar cuando el usuario pida frecuencia/schedule de pipelines, duración promedio, historial de runs, tasa de fallo o volumen de ejecuciones de Fabric, y el MCP de Fabric no exponga esos datos.
---

# Operación de pipelines de Fabric vía API REST (Job Scheduler)

Esta skill complementa al MCP de Fabric para llenar la sección 6 del TRS-9:
frecuencia de ejecución de pipelines y duración promedio, datos que el MCP no
expone. Todo en modo solo lectura.

## Cuándo usar esta skill

- El usuario pide la frecuencia/schedule de los pipelines de un workspace
  (sección 6 del TRS-9).
- El usuario pide duración promedio, tasa de fallo, historial de ejecuciones
  o último error de un pipeline.
- El MCP de Fabric no expone schedules ni historial de runs.

## Requisitos previos

1. **`az login` activo** (el script usa `AzureCliCredential`).
2. Dependencias: `azure-identity` y `requests` (ya disponibles con `uv sync`).
3. **Permisos**: `Item.Read.All` o `DataPipeline.Read.All` con permiso de
   lectura sobre el ítem. SPN soportado. Límite 200/min en Job Scheduler.

## Archivos incluidos

- `scripts/fabric_rest_client.py` — cliente REST compartido (en
  `.coda/skills/fabric-rest-api/scripts/`).
- `scripts/consultar_pipelines.py` — script principal de esta skill.

## Cómo usar esta skill

### 1. Ejecutar la consulta

```bash
# Schedules + historial de todos los pipelines del workspace
uv run python consultar_pipelines.py --workspace <workspaceId>

# Solo schedules de un pipeline específico
uv run python consultar_pipelines.py --workspace <ws> --pipeline <itemId> --solo-schedules

# Solo historial (duración promedio, tasa de fallo, último error)
uv run python consultar_pipelines.py --workspace <ws> --pipeline <itemId> --solo-historial

# Guardar el detalle de runs como CSV
uv run python consultar_pipelines.py --workspace <ws> --output runs.csv
```

El script descubre los pipelines del workspace con `GET
/v1/workspaces/{w}/items?type=DataPipeline` si no se pasa `--pipeline`.

### 2. Qué devuelve

- **Schedules**: por pipeline, lista de schedules con estado (enabled),
  tipo de frecuencia traducido a texto legible (ej. "Cada día a las 02:00,
  zona America/Bogota") a partir de `configuration.type`
  (`Cron`→intervalo en minutos, `Daily`→times, `Weekly`→times+weekdays,
  `Monthly`→times+recurrence+occurrence).
- **Historial**: de `GET /v1/workspaces/{w}/items/{i}/jobs/instances` se
  calculan duración promedio y p95 (`endTimeUtc − startTimeUtc`), tasa de
  fallo, conteo por `invokeType` (Scheduled/Manual) y el último error
  (`failureReason`).

### 3. Limitaciones importantes (comunicar siempre al usuario)

- **jobType de schedules**: la documentación no lo confirma para pipelines.
  El script prueba `Pipeline` primero y, si devuelve error, reintenta con
  `DefaultJob`. Si ambos fallan, reportarlo y verificar en el portal.
- **Historial limitado**: el endpoint genérico devuelve ~100 ejecuciones
  completadas recientes (sin filtro de fecha). No hay retención documentada
  en días; para más historial usar monitoreo.
- **Duración y volumen**: se calculan sobre ese historial reciente; si el
  pipeline corre pocas veces al día, la muestra puede ser pequeña.
- **Detalle por actividad** (opcional): `POST
  /v1/workspaces/{w}/datapipelines/pipelineruns/{jobInstanceId}/queryactivityruns`
  con body `lastUpdatedAfter/lastUpdatedBefore/orderBy/filters` devuelve
  `activityName, activityType, status, durationInMs, error`. Usarlo solo si
  el usuario lo pide explícitamente.
- Throttling: 200/min; ante 429 el cliente reintenta con `Retry-After`.
