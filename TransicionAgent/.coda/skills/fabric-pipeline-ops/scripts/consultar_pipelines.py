"""
Consulta schedules e historial de ejecuciones de pipelines de Fabric
vía API REST - Job Scheduler (solo lectura).

Descubre los pipelines del workspace (o usa uno específico), lista sus
schedules con frecuencia legible y calcula estadísticas del historial de
runs: duración promedio/p95, tasa de fallo, conteo por tipo de invocación y
último error.

Ejemplos:
    uv run python consultar_pipelines.py --workspace <workspaceId>
    uv run python consultar_pipelines.py --workspace <ws> --pipeline <id> --solo-schedules
    uv run python consultar_pipelines.py --workspace <ws> --output runs.csv
"""

import argparse
import csv
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent.parent.parent
        / "fabric-rest-api"
        / "scripts"
    ),
)

from fabric_rest_client import FabricRestClient, FabricRestError  # noqa: E402


def _parsear_fecha(valor: str) -> datetime | None:
    if not valor:
        return None
    try:
        return datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        return None


def _traducir_schedule(schedule: dict) -> str:
    """Convierte configuration del schedule a texto legible."""
    config = schedule.get("configuration") or {}
    tipo = config.get("type", "?")
    zona = config.get("localTimeZoneId", "UTC")
    if tipo == "Cron":
        return f"Cada {config.get('interval', '?')} min ({zona})"
    if tipo == "Daily":
        horas = ", ".join(config.get("times", [])) or "?"
        return f"Cada día a las {horas} ({zona})"
    if tipo == "Weekly":
        horas = ", ".join(config.get("times", [])) or "?"
        dias = ", ".join(config.get("weekdays", [])) or "?"
        return f"Semanal: {dias} a las {horas} ({zona})"
    if tipo == "Monthly":
        horas = ", ".join(config.get("times", [])) or "?"
        return f"Mensual ({config.get('recurrence', '?')}) a las {horas} ({zona})"
    return f"{tipo} ({zona})"


def _obtener_schedules(client: FabricRestClient, workspace_id: str, item_id: str):
    """Lista schedules probando jobType=Pipeline y luego DefaultJob."""
    ultimo_error = None
    for job_type in ("Pipeline", "DefaultJob"):
        try:
            return (
                client.get_all(
                    f"/workspaces/{workspace_id}"
                    f"/items/{item_id}/jobs/{job_type}/schedules"
                ),
                job_type,
            )
        except FabricRestError as error:
            ultimo_error = error
    raise ultimo_error


def _estadisticas_runs(runs: list) -> dict:
    duraciones = []
    fallos = 0
    ultimo_error = ""
    ultimo_run = None
    for run in runs:
        inicio = _parsear_fecha(run.get("startTimeUtc", ""))
        fin = _parsear_fecha(run.get("endTimeUtc", ""))
        if inicio and fin:
            duraciones.append((fin - inicio).total_seconds())
        if run.get("status") == "Failed":
            fallos += 1
            razon = run.get("failureReason") or {}
            ultimo_error = (
                f"{razon.get('errorCode', '')}: {razon.get('message', '')}"
            )
        fin_dt = _parsear_fecha(run.get("endTimeUtc", "")) or datetime.min.replace(
            tzinfo=timezone.utc
        )
        if ultimo_run is None or fin_dt > ultimo_run[0]:
            ultimo_run = (fin_dt, run)

    resumen = {
        "total_runs": len(runs),
        "duracion_promedio_min": None,
        "duracion_p95_min": None,
        "tasa_fallo_pct": None,
        "scheduled": sum(1 for r in runs if r.get("invokeType") == "Scheduled"),
        "manual": sum(1 for r in runs if r.get("invokeType") == "Manual"),
        "ultimo_error": "",
    }
    if duraciones:
        resumen["duracion_promedio_min"] = round(
            statistics.mean(duraciones) / 60, 2
        )
        if len(duraciones) >= 2:
            resumen["duracion_p95_min"] = round(
                statistics.quantiles(duraciones, n=20)[-1] / 60, 2
            )
    if runs:
        resumen["tasa_fallo_pct"] = round(100 * fallos / len(runs), 1)
    if ultimo_error:
        resumen["ultimo_error"] = ultimo_error
    return resumen


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Schedules e historial de pipelines de Fabric (solo lectura)."
    )
    parser.add_argument("--workspace", required=True, help="ID del workspace.")
    parser.add_argument(
        "--pipeline", default=None, help="ID de un pipeline específico (opcional)."
    )
    parser.add_argument(
        "--solo-schedules", action="store_true", help="Solo listar schedules."
    )
    parser.add_argument(
        "--solo-historial", action="store_true", help="Solo historial de runs."
    )
    parser.add_argument(
        "--output", "-o", default=None, help="Guardar detalle de runs como CSV."
    )
    args = parser.parse_args()

    client = FabricRestClient()

    # Descubrir pipelines objetivo
    if args.pipeline:
        objetivos = [{"id": args.pipeline, "displayName": args.pipeline}]
    else:
        try:
            objetivos = client.get_all(
                f"/workspaces/{args.workspace}/items", type="DataPipeline"
            )
        except FabricRestError as error:
            print(f"ERROR listando items del workspace: {error}")
            return 1
    if not objetivos:
        print("Sin pipelines en el workspace (o sin permiso de lectura).")
        return 0

    filas_runs = []
    for item in objetivos:
        item_id = item["id"]
        nombre = item.get("displayName", item_id)

        if not args.solo_historial:
            try:
                schedules, job_type = _obtener_schedules(client, args.workspace, item_id)
                print(f"\n=== {nombre} ({item_id}) — jobType={job_type} ===")
                if not schedules:
                    print("  Sin schedules (¿creados desde la UI? verificar portal).")
                for schedule in schedules:
                    estado = "ON" if schedule.get("enabled") else "OFF"
                    print(f"  [{estado}] {_traducir_schedule(schedule)}")
            except FabricRestError as error:
                print(f"\n=== {nombre} ({item_id}) ===\n  ERROR schedules: {error}")

        if not args.solo_schedules:
            try:
                runs = client.get_all(
                    f"/workspaces/{args.workspace}/items/{item_id}/jobs/instances"
                )
                resumen = _estadisticas_runs(runs)
                print(f"  Runs recientes: {resumen['total_runs']}"
                      f" (scheduled={resumen['scheduled']}, manual={resumen['manual']})")
                if resumen["duracion_promedio_min"] is not None:
                    print(f"  Duración promedio: {resumen['duracion_promedio_min']} min"
                          f" | p95: {resumen['duracion_p95_min']} min")
                if resumen["tasa_fallo_pct"] is not None:
                    print(f"  Tasa de fallo: {resumen['tasa_fallo_pct']}%")
                if resumen["ultimo_error"]:
                    print(f"  Último error: {resumen['ultimo_error'][:200]}")
                for run in runs:
                    filas_runs.append(
                        {
                            "pipeline": nombre,
                            "status": run.get("status", ""),
                            "invokeType": run.get("invokeType", ""),
                            "startTimeUtc": run.get("startTimeUtc", ""),
                            "endTimeUtc": run.get("endTimeUtc", ""),
                            "failureReason": (run.get("failureReason") or {}).get(
                                "message", ""
                            ),
                        }
                    )
            except FabricRestError as error:
                print(f"  ERROR historial: {error}")

    print(
        "\nNOTA: el historial está limitado a ~100 ejecuciones completadas "
        "recientes; para más historial usar monitoreo."
    )

    if args.output and filas_runs:
        with open(args.output, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(filas_runs[0].keys()))
            writer.writeheader()
            writer.writerows(filas_runs)
        print(f"\nCSV guardado en: {Path(args.output).resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
