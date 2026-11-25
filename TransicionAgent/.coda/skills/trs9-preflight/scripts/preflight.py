"""
Preflight del flujo de transición TRS-9: verifica (y opcionalmente instala) lo
necesario para correr las skills. Solo usa la librería estándar, así corre aunque
las dependencias del proyecto aún no estén instaladas.

Uso (desde la raíz de TransicionAgent/):

    python .coda/skills/trs9-preflight/scripts/preflight.py            # solo verifica
    python .coda/skills/trs9-preflight/scripts/preflight.py --instalar # + instala lo que se pueda

`--instalar` hace, sin tocar nada del sistema operativo:
  - `uv sync`                          (dependencias Python del proyecto)
  - `uv tool install ms-fabric-cli`    (comando `fab`) si falta
Lo que requiere instalación de sistema (Python, uv, Azure CLI, Node.js,
driver ODBC, .NET) NO se instala: el script indica el paso exacto.
`az login` / `fab auth login` tampoco se ejecutan solos (abren el navegador).

Códigos de salida: 0 = todo lo requerido OK; 1 = falta algo requerido.
"""

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3].parent  # raíz de TransicionAgent/
ENV_FILE = ROOT / ".coda" / "skills" / "fabric-odbc-query" / "scripts" / ".env"
ENV_KEYS = ("FABRIC_DRIVER", "FABRIC_SERVER", "FABRIC_DATABASE")
IMPORTS = {
    "pyodbc": "pyodbc", "pandas": "pandas", "dotenv": "python-dotenv",
    "msal": "msal", "azure.identity": "azure-identity", "requests": "requests",
    "openpyxl": "openpyxl", "yaml": "pyyaml",
}
resultados = []  # (estado, nombre, detalle, requerido)


def correr(cmd, timeout=90):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:  # noqa: BLE001
        return 99, str(e)


def registrar(ok, nombre, detalle, requerido=True, warn=False):
    estado = "OK " if ok else ("AVISO" if (warn or not requerido) else "FALTA")
    resultados.append((estado, nombre, detalle, requerido))


def chequear_herramientas(instalar):
    v = sys.version_info
    registrar(v >= (3, 10), "Python", f"{v.major}.{v.minor}.{v.micro}" +
              ("" if v >= (3, 10) else " (se requiere 3.10+; uv puede gestionar 3.13)"))

    uv = shutil.which("uv")
    registrar(bool(uv), "uv", correr([uv, "--version"])[1] if uv else
              "no instalado -> `pip install uv` (o https://docs.astral.sh/uv/)")

    # Dependencias Python del proyecto
    if uv and instalar:
        print("› uv sync ...")
        rc, out = correr([uv, "sync"], timeout=600)
        if rc != 0:
            print(out[-600:])
    faltan = []
    for mod, paquete in IMPORTS.items():
        rc, _ = correr([sys.executable, "-c", f"import {mod}"], timeout=60)
        if rc != 0:
            faltan.append(paquete)
    rc_venv = False
    if uv:
        # ¿el entorno del proyecto (.venv) tiene todo?
        rc, out = correr([uv, "run", "--no-sync", "python", "-c",
                          "import " + ",".join(IMPORTS)], timeout=120)
        rc_venv = rc == 0
    registrar(rc_venv or not faltan, "Dependencias Python",
              "importables" if (rc_venv or not faltan) else
              "faltan " + ", ".join(faltan) + " -> ejecuta `uv sync` (o este script con --instalar)")

    fab = shutil.which("fab")
    if not fab and uv and instalar:
        print("› uv tool install ms-fabric-cli ...")
        correr([uv, "tool", "install", "ms-fabric-cli"], timeout=600)
        fab = shutil.which("fab")
        if not fab:  # uv tool bin puede no estar en PATH de esta sesión
            cand = Path.home() / ".local" / "bin" / ("fab.exe" if os.name == "nt" else "fab")
            fab = str(cand) if cand.exists() else None
    if fab:
        rc, out = correr([fab, "--version"])
        registrar(rc == 0, "fabric-cli (fab)", out.splitlines()[0] if out else "ok", requerido=False)
        rc, out = correr([fab, "auth", "status"])
        sesion = rc == 0 and "not" not in out.lower()[:80]
        registrar(sesion, "fab: sesión", "activa" if sesion else
                  "sin sesión -> `fab auth login` (abre el navegador)", requerido=False)
    else:
        registrar(False, "fabric-cli (fab)",
                  "no instalado -> `uv tool install ms-fabric-cli` (o --instalar)", requerido=False)

    az = shutil.which("az")
    if az:
        rc, out = correr([az, "account", "show", "--query", "user.name", "-o", "tsv"], timeout=120)
        registrar(rc == 0, "Azure CLI: sesión", out if rc == 0 else
                  "sin sesión -> `az login` (tenant Ecopetrol)")
    else:
        registrar(False, "Azure CLI (az)", "no instalado -> https://aka.ms/installazurecli")

    node = shutil.which("node") and shutil.which("npx")
    registrar(bool(node), "Node.js / npx", "ok (MCP Azure DevOps)" if node else
              "no instalado -> Node.js LTS (necesario para publicar en la wiki vía MCP)")

    dnx = shutil.which("dnx")
    registrar(bool(dnx), "dnx (.NET 10 SDK)", "ok (MCP Fabric)" if dnx else
              "no encontrado; solo bloquea si el MCP de Fabric no carga (instalar .NET 10 SDK)",
              requerido=False)

    # Driver ODBC (solo necesario para consultas SQL)
    drivers = []
    if platform.system() == "Windows":
        rc, out = correr(["powershell", "-NoProfile", "-Command",
                          "Get-OdbcDriver | Select-Object -ExpandProperty Name"])
        drivers = [l.strip() for l in out.splitlines() if re.search(r"ODBC Driver \d+ for SQL Server", l)]
    elif shutil.which("odbcinst"):
        rc, out = correr(["odbcinst", "-q", "-d"])
        drivers = [l.strip("[] ") for l in out.splitlines() if "SQL Server" in l]
    drivers = sorted(set(drivers))
    registrar(bool(drivers), "Driver ODBC SQL Server",
              ", ".join(drivers) if drivers else
              "no encontrado -> instalar 'ODBC Driver 18 for SQL Server' (solo para consultas SQL)",
              requerido=False)

    # .env del skill ODBC (solo nombres de claves, nunca valores)
    if ENV_FILE.exists():
        claves = set(re.findall(r"^\s*([A-Z_]+)\s*=", ENV_FILE.read_text(encoding="utf-8-sig"), re.M))
        falt = [k for k in ENV_KEYS if k not in claves]
        registrar(not falt, ".env (ODBC)", "claves presentes" if not falt else
                  "faltan: " + ", ".join(falt), requerido=False)
    else:
        registrar(False, ".env (ODBC)", "no existe; solo se necesita para consultas SQL "
                  "(plantilla: .coda/skills/fabric-odbc-query/scripts/env.example)", requerido=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--instalar", action="store_true",
                    help="ejecuta `uv sync` e instala `fab` con uv si faltan")
    args = ap.parse_args()
    os.chdir(ROOT)
    sys.stdout.reconfigure(encoding="utf-8")
    chequear_herramientas(args.instalar)

    print(f"\nPreflight TRS-9  ({platform.system()}, raíz: {ROOT})\n")
    ancho = max(len(r[1]) for r in resultados)
    for estado, nombre, detalle, _ in resultados:
        print(f"  [{estado}] {nombre.ljust(ancho)}  {detalle}")
    faltantes = [r for r in resultados if r[0] == "FALTA"]
    avisos = [r for r in resultados if r[0] == "AVISO"]
    print()
    if faltantes:
        print(f"{len(faltantes)} requisito(s) obligatorio(s) sin cumplir (marcados FALTA).")
    else:
        print("Requisitos obligatorios OK.")
    if avisos:
        print(f"{len(avisos)} aviso(s): opcionales o dependen del paso a ejecutar.")
    return 1 if faltantes else 0


if __name__ == "__main__":
    sys.exit(main())
