"""
Conexiones que REALMENTE usan los pipelines de uno o más workspaces (solo
lectura), cruzadas con los datos de la conexión (tipo de credencial,
conectividad, gateway, host/BD). Es lo que necesita la sección
"Fuentes de Datos y Conexiones" del TRS-9, sin listar las conexiones del tenant
que el workspace no usa.

Para cada DataPipeline: GET /workspaces/{ws}/items/{pipeline}/connections
Cruce por id con GET /connections y nombre de gateway con GET /gateways.

Uso (desde la raíz de TransicionAgent/):

    uv run python .coda/skills/fabric-connections-audit/scripts/conexiones_workspace.py \
        --workspace "WS-FB-DEV-ProyectosOperativos-GLB" \
        --workspace "WS-FB-DEV-DMProyectosGold" \
        --con-gateways --output .coda/tmp/conexiones-usadas.json

Rutas del cliente REST: son relativas a la base `/v1` (usa `/connections`, no
`/v1/connections`; esto último da 404).
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent.parent / "fabric-rest-api" / "scripts"),
)
from fabric_rest_client import FabricRestClient, FabricRestError  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
GUID_RE = re.compile(r"^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", action="append", required=True, help="Nombre exacto o GUID")
    ap.add_argument("--con-gateways", action="store_true", help="checkStatus de cada gateway usado")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    c = FabricRestClient()
    workspaces = c.get_all("/workspaces")
    todas = {x["id"]: x for x in c.get_all("/connections")}
    try:
        gateways = {g["id"]: g for g in c.get_all("/gateways")}
    except FabricRestError:
        gateways = {}

    usadas = {}  # connection id -> {datos, pipelines:[...]}
    errores = []
    for ref in args.workspace:
        ws = next(
            (w for w in workspaces
             if w["id"].lower() == ref.lower() or w["displayName"].lower() == ref.lower()),
            None,
        )
        if not ws:
            print(f"ERROR: workspace '{ref}' no encontrado (nombre exacto o GUID).")
            return 2
        pipelines = c.get_all(f"/workspaces/{ws['id']}/items", type="DataPipeline")
        print(f"{ws['displayName']}: {len(pipelines)} pipelines")
        for p in pipelines:
            try:
                conns = c.get_all(f"/workspaces/{ws['id']}/items/{p['id']}/connections")
            except FabricRestError as e:
                errores.append(f"{ws['displayName']}/{p['displayName']}: {str(e)[:160]}")
                continue
            for cn in conns:
                reg = usadas.setdefault(cn["id"], {"pipelines": []})
                reg["pipelines"].append(f"{ws['displayName']}/{p['displayName']}")

    salida = []
    for cid, reg in usadas.items():
        full = todas.get(cid, {})
        det = full.get("connectionDetails") or {}
        cred = (full.get("credentialDetails") or {}).get("credentialType", "")
        rec = full.get("connectionRecency") or {}
        gid = (full.get("gatewayId") or "").strip()
        gw = gateways.get(gid, {})
        fila = {
            "id": cid,
            "nombre": full.get("displayName", "(no visible)"),
            "connectivityType": full.get("connectivityType", ""),
            "credentialType": cred,
            "tipo": det.get("type", ""),
            "path": det.get("path", ""),
            "gatewayId": gid,
            "gateway": gw.get("displayName") or (
                "(gateway no visible por API; verificar en portal)" if gid else ""
            ),
            "gatewayStatus": "",
            "ultimoUsoCredencial": rec.get("lastCredentialUsedDateTime", ""),
            "pipelines": sorted(set(reg["pipelines"])),
        }
        if args.con_gateways and gid and gw:
            try:
                fila["gatewayStatus"] = c.check_gateway_status(gid).get("status", "")
            except FabricRestError as e:
                fila["gatewayStatus"] = f"error: {str(e)[:80]}"
        salida.append(fila)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps({"conexiones": salida, "errores": errores}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"\n{len(salida)} conexiones usadas:")
    for f in salida:
        print(f"  - {f['nombre']} | {f['connectivityType']} | {f['credentialType']} | "
              f"{f['tipo']} {f['path']} | gw: {f['gateway']} {f['gatewayStatus']} | "
              f"{len(f['pipelines'])} pipelines")
    if errores:
        print(f"\n{len(errores)} pipelines sin poder leer conexiones (ver JSON).")
    print(f"Guardado: {out}")
    print("NOTA: vencimiento de credenciales no está disponible por API; verificar en el portal.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
