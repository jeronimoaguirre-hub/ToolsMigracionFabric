"""
Recolecta (solo lectura) el inventario de uno o más workspaces de Fabric y lo
guarda en un JSON para llenar el Inventario Fabric (xlsx) y el TRS-9.

Por workspace obtiene:
  - items (GET /workspaces/{id}/items) con su ruta de carpeta completa
    (GET /workspaces/{id}/folders?recursive=true + folderId del item);
  - por cada DataPipeline: schedules (activo/deshabilitado) y estadísticas de
    runs (duración promedio, nº de runs, tasa de fallo);
  - por cada Lakehouse: tablas Delta por esquema, vía OneLake (DFS), porque
    la API de tablas de Fabric falla en lakehouses con esquemas
    (UnsupportedOperationForSchema).

Uso (desde la raíz de TransicionAgent/):

    uv run python .coda/skills/fabric-inventory/scripts/recolectar_workspace.py \
        --workspace "Silver=WS-FB-DEV-ProyectosOperativos-GLB" \
        --workspace "Gold=WS-FB-DEV-DMProyectosGold" \
        --output .coda/tmp/inventario-datos.json

`--workspace` acepta nombre exacto o GUID, opcionalmente con prefijo
`Capa=` (Bronze|Silver|Gold) que se usa como capa por defecto de los items del
workspace (cada item puede sobrescribirla por prefijo brz/slv/gld en su nombre).
Si un nombre no existe NO se adivina: el script lista los más parecidos y
termina con código 2.
"""

import argparse
import difflib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import requests

_SKILLS = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_SKILLS / "fabric-rest-api" / "scripts"))
sys.path.insert(0, str(_SKILLS / "fabric-pipeline-ops" / "scripts"))

from fabric_rest_client import FabricRestClient, FabricRestError  # noqa: E402
from consultar_pipelines import (  # noqa: E402
    _estadisticas_runs,
    _obtener_schedules,
    _traducir_schedule,
)

sys.stdout.reconfigure(encoding="utf-8")

GUID_RE = re.compile(r"^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$")
ONELAKE = "https://onelake.dfs.fabric.microsoft.com"
STORAGE_SCOPE = "https://storage.azure.com/.default"
CAPAS = {"bronze": "Bronze", "silver": "Silver", "gold": "Gold"}

def capa_por_nombre(nombre: str) -> str:
    n = nombre.lower()
    if re.search(r"(^|[_\-])(brz|bronze|bronce)([_\-]|$)", n):
        return "Bronze"
    if re.search(r"(^|[_\-])(slv|silver)([_\-]|$)", n):
        return "Silver"
    if re.search(r"(^|[_\-])(gld|gold)([_\-]|$)", n):
        return "Gold"
    return ""


def resolver_workspace(client, workspaces, ref):
    if GUID_RE.match(ref):
        for w in workspaces:
            if w["id"].lower() == ref.lower():
                return w
        raise SystemExit(f"ERROR: no tienes acceso al workspace con id {ref}.")
    for w in workspaces:
        if w["displayName"].lower() == ref.lower():
            return w
    cercanos = difflib.get_close_matches(
        ref, [w["displayName"] for w in workspaces], n=5, cutoff=0.6
    )
    print(f"ERROR: no existe un workspace llamado exactamente '{ref}'.")
    if cercanos:
        print("Más parecidos (confirma con el usuario, no adivines):")
        for c in cercanos:
            print(f"  - {c}")
    raise SystemExit(2)


def rutas_de_carpetas(client, ws_id):
    carpetas = client.get_all(f"/workspaces/{ws_id}/folders", recursive="true")
    por_id = {c["id"]: c for c in carpetas}

    def ruta(fid):
        partes = []
        while fid and fid in por_id:
            partes.insert(0, por_id[fid]["displayName"])
            fid = por_id[fid].get("parentFolderId")
        return "/".join(partes)

    return {fid: ruta(fid) for fid in por_id}


def _onelake_list(session, token, ws_id, directorio):
    """Lista hijos directos de `directorio` (relativo al workspace)."""
    resultados, cont = [], None
    while True:
        params = {
            "resource": "filesystem",
            "directory": directorio,
            "recursive": "false",
        }
        if cont:
            params["continuation"] = cont
        r = session.get(
            f"{ONELAKE}/{ws_id}",
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
        )
        if r.status_code == 404:
            return []
        if r.status_code != 200:
            raise FabricRestError(
                f"OneLake {directorio} -> HTTP {r.status_code}: {r.text[:200]}",
                status_code=r.status_code,
            )
        resultados.extend(r.json().get("paths", []))
        cont = r.headers.get("x-ms-continuation")
        if not cont:
            return resultados


def tablas_lakehouse(client, ws_id, lh_id):
    """Devuelve {esquema: [tablas]}; esquema 'dbo'/'' según el lakehouse."""
    token = client.get_token(STORAGE_SCOPE)
    s = requests.Session()
    base = f"{lh_id}/Tables"
    hijos = [
        p["name"].split("/")[-1]
        for p in _onelake_list(s, token, ws_id, base)
        if str(p.get("isDirectory", "")).lower() == "true"
    ]
    out = {}
    for h in hijos:
        if h.startswith("_"):
            continue
        sub = _onelake_list(s, token, ws_id, f"{base}/{h}")
        nombres = [p["name"].split("/")[-1] for p in sub]
        if "_delta_log" in nombres:  # h es una tabla (lakehouse sin esquemas)
            out.setdefault("", []).append(h)
        else:  # h es un esquema
            out[h] = sorted(
                p["name"].split("/")[-1]
                for p in sub
                if str(p.get("isDirectory", "")).lower() == "true"
                and not p["name"].split("/")[-1].startswith("_")
            )
    return out


def carpetas_files(client, ws_id, lh_id, profundidad=3):
    """Rutas de carpetas de `Files/` hasta `profundidad` niveles (solo directorios)."""
    token = client.get_token(STORAGE_SCOPE)
    s = requests.Session()
    rutas = []

    def rec(directorio, nivel):
        if nivel > profundidad:
            return
        for p in _onelake_list(s, token, ws_id, directorio):
            if str(p.get("isDirectory", "")).lower() != "true":
                continue
            rel = p["name"].split("/", 1)[1] if "/" in p["name"] else p["name"]
            rutas.append(rel)
            rec(p["name"], nivel + 1)

    rec(f"{lh_id}/Files", 1)
    return rutas


def recolectar(client, ws, capa_defecto, con_tablas, con_pipelines):
    ws_id = ws["id"]
    print(f"\n=== {ws['displayName']} ({ws_id}) ===")
    rutas = rutas_de_carpetas(client, ws_id)
    items = client.get_all(f"/workspaces/{ws_id}/items")
    print(f"  items: {len(items)} | carpetas: {len(rutas)}")
    res = {
        "nombre": ws["displayName"],
        "id": ws_id,
        "url": f"https://app.fabric.microsoft.com/groups/{ws_id}",
        "capacityId": ws.get("capacityId"),
        "capa_defecto": capa_defecto,
        "items": [],
        "pipelines": {},
        "tablas": {},
        "archivos": {},
        "avisos": [],
    }
    for it in items:
        res["items"].append(
            {
                "id": it["id"],
                "tipo": it["type"],
                "nombre": it["displayName"],
                "descripcion": it.get("description") or "",
                "carpeta": rutas.get(it.get("folderId"), ""),
                "capa": capa_por_nombre(it["displayName"]) or capa_defecto,
            }
        )

    if con_pipelines:
        for it in [i for i in items if i["type"] == "DataPipeline"]:
            info = {"schedules": [], "runs": None, "aviso": ""}
            try:
                schedules, _ = _obtener_schedules(client, ws_id, it["id"])
                info["schedules"] = [
                    {
                        "activo": bool(s.get("enabled")),
                        "texto": _traducir_schedule(s),
                    }
                    for s in schedules
                ]
            except FabricRestError as e:
                info["aviso"] = f"schedules: {str(e)[:150]}"
            try:
                runs = client.get_all(
                    f"/workspaces/{ws_id}/items/{it['id']}/jobs/instances"
                )
                info["runs"] = _estadisticas_runs(runs)
            except FabricRestError as e:
                info["aviso"] += f" runs: {str(e)[:150]}"
            res["pipelines"][it["id"]] = info
        print(f"  pipelines procesados: {len(res['pipelines'])}")

    if con_tablas:
        for it in [i for i in items if i["type"] == "Lakehouse"]:
            try:
                res["archivos"][it["id"]] = carpetas_files(client, ws_id, it["id"])
            except FabricRestError as e:
                res["avisos"].append(f"Files de {it['displayName']}: {e}")
            try:
                res["tablas"][it["id"]] = tablas_lakehouse(client, ws_id, it["id"])
                n = sum(len(v) for v in res["tablas"][it["id"]].values())
                print(f"  tablas en {it['displayName']}: {n}")
            except FabricRestError as e:
                res["avisos"].append(f"tablas de {it['displayName']}: {e}")
                print(f"  AVISO tablas {it['displayName']}: {e}")
        for it in [i for i in items if i["type"] == "Warehouse"]:
            res["avisos"].append(
                f"Warehouse {it['displayName']}: sus tablas/vistas no se listan por "
                "API; consultarlas por SQL (skill fabric-odbc-query, INFORMATION_SCHEMA)."
            )
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--workspace",
        action="append",
        required=True,
        help='[Capa=]nombre-o-GUID. Repetible. Ej: "Silver=WS-FB-DEV-X"',
    )
    ap.add_argument("--output", required=True, help="JSON de salida")
    ap.add_argument("--sin-tablas", action="store_true")
    ap.add_argument("--sin-pipelines", action="store_true")
    args = ap.parse_args()

    client = FabricRestClient()
    todos = client.get_all("/workspaces")
    resultado = {
        "generado": datetime.now().isoformat(timespec="seconds"),
        "workspaces": [],
    }
    for ref in args.workspace:
        capa = ""
        if "=" in ref:
            pref, resto = ref.split("=", 1)
            if pref.strip().lower() in CAPAS:
                capa, ref = CAPAS[pref.strip().lower()], resto
        ws = resolver_workspace(client, todos, ref.strip())
        resultado["workspaces"].append(
            recolectar(
                client, ws, capa, not args.sin_tablas, not args.sin_pipelines
            )
        )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nGuardado: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
