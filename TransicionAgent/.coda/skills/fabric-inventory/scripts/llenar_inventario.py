"""
Llena la plantilla `TRS - 9/Inventario_Fabric_WS_XXX.template.xlsx` (hoja
"Lista de objetos") con el JSON generado por `recolectar_workspace.py`.

Columnas de la plantilla (11, fila 4 = encabezados, datos desde la fila 5):
  A Ambiente | B Capa | C Nombre de Carpeta | D Subcarpeta | E Nombre |
  F Tipo de Objeto | G Estado (nuevo/actualizado) | H Descripción |
  I Frecuencia de actualización | J Duración promedio (QA) | K Duración promedio (QA)

Uso (desde la raíz de TransicionAgent/):

    uv run python .coda/skills/fabric-inventory/scripts/llenar_inventario.py \
        --datos .coda/tmp/inventario-datos.json \
        --salida Inventario_Fabric_DMProyectos.xlsx \
        --nombre-workspace "WS-FB-DEV-ProyectosOperativos-GLB / WS-FB-DEV-DMProyectosGold" \
        --ambiente DEV/QA --estado Nuevo

Reglas de mapeo:
  - Nombre de Carpeta / Subcarpeta: la ruta de carpeta del item en Fabric; la
    última carpeta es la Subcarpeta y el resto el Nombre de Carpeta
    (ej. `Ingesta/HANA-DM_PROYECTOS/Notebooks` -> `Ingesta/HANA-DM_PROYECTOS` + `Notebooks`).
    Item en la raíz -> `(raíz)` + `-`.
  - Tablas Delta de un lakehouse: carpeta `<lakehouse>/Tables`, subcarpeta = esquema.
  - Capa: por prefijo brz/slv/gld del nombre del item; si no, la del workspace.
  - Lo que no se puede saber queda como `<DATO REQUERIDO: ...>`.
"""

import argparse
import json
import sys
from copy import copy
from pathlib import Path

import openpyxl

sys.stdout.reconfigure(encoding="utf-8")

DATO = "<DATO REQUERIDO: {}>"
DESCRIPCIONES_BASURA = {"", "new notebook", "new pipeline", "notebook", "environment"}
ORDEN_TIPO = {
    "Lakehouse": 0, "Warehouse": 1, "SQLEndpoint": 2, "Environment": 3,
    "VariableLibrary": 4, "DataPipeline": 5, "Notebook": 6, "Tabla Delta": 7,
}


def partir_carpeta(ruta: str):
    if not ruta:
        return "(raíz)", "-"
    partes = ruta.split("/")
    if len(partes) == 1:
        return partes[0], "-"
    return "/".join(partes[:-1]), partes[-1]


def fmt_duracion(runs):
    if not runs or not runs.get("total_runs"):
        return "Sin ejecuciones"
    m = runs.get("duracion_promedio_min")
    if m is None:
        return "Sin ejecuciones"
    txt = f"{round(m * 60)} segundos" if m < 1 else f"{round(m, 1)} min"
    return f"{txt} ({runs['total_runs']} runs)"


def fmt_frecuencia(info):
    if not info:
        return "No aplica"
    sch = info.get("schedules") or []
    if not sch:
        return "Sin schedule (manual)"
    return "; ".join(
        f"{s['texto']} — {'ACTIVO' if s['activo'] else 'deshabilitado'}" for s in sch
    )


def construir_filas(datos, ambiente, estado, descripciones=None):
    """`descripciones`: {nombre_de_objeto: texto} redactado por el agente a
    partir de lo que leyó del item; solo reemplaza descripciones vacías."""
    descripciones = descripciones or {}
    filas = []
    for ws in datos["workspaces"]:
        nombres_lh = {i["id"]: i for i in ws["items"] if i["tipo"] == "Lakehouse"}
        for it in ws["items"]:
            carpeta, sub = partir_carpeta(it["carpeta"])
            desc = it["descripcion"].strip()
            if desc.lower() in DESCRIPCIONES_BASURA:
                desc = descripciones.get(it["nombre"]) or DATO.format("DESCRIPCION")
            info = ws["pipelines"].get(it["id"]) if it["tipo"] == "DataPipeline" else None
            filas.append(
                {
                    "ws": ws["nombre"],
                    "capa": it["capa"] or DATO.format("CAPA BRONZE/SILVER/GOLD"),
                    "carpeta": carpeta,
                    "sub": sub,
                    "nombre": it["nombre"],
                    "tipo": it["tipo"],
                    "desc": desc,
                    "frec": fmt_frecuencia(info),
                    "dur": fmt_duracion(info["runs"]) if info else "No aplica",
                }
            )
        for lh_id, esquemas in ws["tablas"].items():
            lh = nombres_lh[lh_id]
            for esquema, tablas in esquemas.items():
                for t in tablas:
                    filas.append(
                        {
                            "ws": ws["nombre"],
                            "capa": lh["capa"] or DATO.format("CAPA BRONZE/SILVER/GOLD"),
                            "carpeta": f"{lh['nombre']}/Tables",
                            "sub": esquema or "-",
                            "nombre": t,
                            "tipo": "Tabla Delta",
                            "desc": f"Tabla Delta del esquema {esquema}" if esquema
                            else "Tabla Delta del lakehouse",
                            "frec": "No aplica",
                            "dur": "No aplica",
                        }
                    )
    capas = {"Bronze": 0, "Silver": 1, "Gold": 2}
    filas.sort(
        key=lambda f: (
            capas.get(f["capa"], 9), f["ws"], f["carpeta"], f["sub"],
            ORDEN_TIPO.get(f["tipo"], 8), f["nombre"],
        )
    )
    return [
        [ambiente, f["capa"], f["carpeta"], f["sub"], f["nombre"], f["tipo"], estado,
         f["desc"], f["frec"], f["dur"], f["dur"]]
        for f in filas
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--datos", required=True)
    ap.add_argument("--plantilla", default="TRS - 9/Inventario_Fabric_WS_XXX.template.xlsx")
    ap.add_argument("--salida", required=True)
    ap.add_argument("--nombre-workspace", required=True)
    ap.add_argument("--responsable", default=DATO.format("RESPONSABLE DEL DOMINIO"))
    ap.add_argument("--ambiente", default="DEV/QA")
    ap.add_argument("--estado", default="Nuevo", help="Nuevo | Actualizado")
    ap.add_argument(
        "--descripciones",
        help="JSON {nombre_objeto: descripción} con descripciones redactadas "
        "por el agente para objetos que en Fabric no tienen descripción.",
    )
    args = ap.parse_args()

    datos = json.loads(Path(args.datos).read_text(encoding="utf-8"))
    descripciones = (
        json.loads(Path(args.descripciones).read_text(encoding="utf-8"))
        if args.descripciones else None
    )
    filas = construir_filas(datos, args.ambiente, args.estado, descripciones)

    wb = openpyxl.load_workbook(args.plantilla)
    ws = wb["Lista de objetos"]
    ws["A1"] = None  # la plantilla trae "Ejemplo " como marca
    ws["D1"] = args.nombre_workspace
    ws["D2"] = args.responsable

    # Encabezados en fila 4: validar que la plantilla sea la esperada.
    enc = [str(ws.cell(4, c).value or "").strip() for c in range(1, 12)]
    if enc[0] != "Ambiente" or "Tipo de Objeto" not in enc[5]:
        print(f"ERROR: la fila 4 no tiene los encabezados esperados: {enc}")
        return 1

    estilos = [copy(ws.cell(5, c)._style) for c in range(1, 12)]
    # Limpiar ejemplos y filas vacías previas (valores, no formato).
    for r in range(5, max(ws.max_row, 5 + len(filas)) + 1):
        for c in range(1, 12):
            ws.cell(r, c).value = None
    for i, fila in enumerate(filas):
        for c, v in enumerate(fila, start=1):
            celda = ws.cell(5 + i, c, v)
            celda._style = copy(estilos[c - 1])

    anchos = {1: 10, 2: 9, 3: 34, 4: 22, 5: 42, 6: 16, 7: 16, 8: 60, 9: 38, 10: 22, 11: 22}
    for c, w in anchos.items():
        ws.column_dimensions[openpyxl.utils.get_column_letter(c)].width = w

    wb.save(args.salida)

    # Verificación: releer y contar.
    wb2 = openpyxl.load_workbook(args.salida)
    s2 = wb2["Lista de objetos"]
    n = pend = 0
    for r in range(5, s2.max_row + 1):
        vals = [s2.cell(r, c).value for c in range(1, 12)]
        if all(v is None for v in vals):
            continue
        n += 1
        assert all(v not in (None, "") for v in vals), f"fila {r} incompleta: {vals}"
        pend += sum(1 for v in vals if "<DATO REQUERIDO" in str(v))
    print(f"OK: {n} filas x 11 columnas escritas en {args.salida}")
    print(f"Celdas pendientes (<DATO REQUERIDO>): {pend} (+ D2 si el responsable no se dio)")
    por_tipo = {}
    for f in filas:
        por_tipo[f[5]] = por_tipo.get(f[5], 0) + 1
    print("Por tipo:", dict(sorted(por_tipo.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
