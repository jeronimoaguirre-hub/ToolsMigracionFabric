"""
Audita las conexiones de Microsoft Fabric vía API REST (solo lectura).

Lista las conexiones visibles por el usuario autenticado (az login), con su
tipo de conectividad, tipo de credencial, gateway asociado y recencia de uso.
Opcionalmente consulta el estado de los gateways (Online/Offline) con
checkStatus.

Ejemplos:
    uv run python auditar_conexiones.py
    uv run python auditar_conexiones.py --filtro "Ventas" --con-gateways
    uv run python auditar_conexiones.py --output conexiones.csv
"""

import argparse
import csv
import sys
from pathlib import Path

# El cliente compartido vive en la skill fabric-rest-api.
sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent.parent.parent
        / "fabric-rest-api"
        / "scripts"
    ),
)

from fabric_rest_client import FabricRestClient, FabricRestError  # noqa: E402


def _resumir_gateway(conexion: dict) -> str:
    gateway_id = (conexion.get("gatewayId") or "").strip()
    if not gateway_id:
        return ""
    connectivity = conexion.get("connectivityType", "")
    # En conexiones cloud el gatewayId es el gateway virtual; no lo auditamos.
    if connectivity in ("ShareableCloud", "Automatic", "None", "PersonalCloud"):
        return f"{gateway_id} (virtual)"
    return gateway_id


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audita conexiones de Fabric vía API REST (solo lectura)."
    )
    parser.add_argument(
        "--filtro", default=None, help="Filtrar por texto en el nombre de la conexión."
    )
    parser.add_argument(
        "--con-gateways",
        action="store_true",
        help="Consultar estado de gateways (checkStatus; máx 10/min, puede tardar).",
    )
    parser.add_argument(
        "--output", "-o", default=None, help="Guardar resultado como CSV."
    )
    args = parser.parse_args()

    client = FabricRestClient()
    try:
        conexiones = client.get_all("/connections")
    except FabricRestError as error:
        print(f"ERROR: {error}")
        if getattr(error, "status_code", None) == 401:
            print("Sesión de az login expirada o sin permisos: ejecuta `az login`.")
        return 1

    if args.filtro:
        texto = args.filtro.lower()
        conexiones = [
            c for c in conexiones if texto in (c.get("displayName") or "").lower()
        ]

    # Estado de gateways (solo los reales, no los virtuales de conexiones cloud)
    estados_gateway: dict = {}
    if args.con_gateways:
        gateway_ids = {
            c.get("gatewayId")
            for c in conexiones
            if c.get("gatewayId")
            and c.get("connectivityType")
            not in ("ShareableCloud", "Automatic", "None", "PersonalCloud")
        }
        for gateway_id in sorted(gateway_ids):
            try:
                detalle = client.get(f"/gateways/{gateway_id}")
                estado = client.check_gateway_status(gateway_id)
                estados_gateway[gateway_id] = {
                    "nombre": detalle.get("displayName", ""),
                    "tipo": detalle.get("type", ""),
                    "version": detalle.get("version", ""),
                    "status": estado.get("status", "?"),
                    "upgrade": estado.get("gatewayUpgradeState", "?"),
                }
            except FabricRestError as error:
                estados_gateway[gateway_id] = {"error": str(error)}

    filas = []
    for conexion in conexiones:
        gateway_id = (conexion.get("gatewayId") or "").strip()
        info_gw = estados_gateway.get(gateway_id, {})
        recencia = conexion.get("connectionRecency") or {}
        credenciales = conexion.get("credentialDetails") or {}
        filas.append(
            {
                "nombre": conexion.get("displayName", ""),
                "connectivityType": conexion.get("connectivityType", ""),
                "credentialType": credenciales.get("credentialType", ""),
                "gateway": info_gw.get(
                    "nombre", gateway_id if gateway_id else ""
                ),
                "gateway_status": info_gw.get("status", ""),
                "gateway_version": info_gw.get("version", ""),
                "last_credential_used": recencia.get(
                    "lastCredentialUsedDateTime", ""
                ),
                "last_bound": recencia.get("lastBoundDateTime", ""),
            }
        )

    # Salida en consola
    if not filas:
        print("Sin conexiones visibles (¿permisos insuficientes?).")
        return 0

    anchos = {
        clave: max(len(str(fila.get(clave, ""))) for fila in filas + [{}])
        for clave in filas[0]
    }
    encabezado = list(filas[0].keys())
    print(" | ".join(str(k).ljust(anchos[k]) for k in encabezado))
    print("-+-".join("-" * anchos[k] for k in encabezado))
    for fila in filas:
        print(" | ".join(str(fila[k]).ljust(anchos[k]) for k in encabezado))

    print(
        "\nNOTA: el vencimiento de credenciales no está disponible por API; "
        "verificar en el portal de Fabric (Manage connections and gateways)."
    )

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=encabezado)
            writer.writeheader()
            writer.writerows(filas)
        print(f"\nCSV guardado en: {Path(args.output).resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
