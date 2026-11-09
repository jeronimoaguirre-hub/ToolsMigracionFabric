"""
Script para consultar el Warehouse de Microsoft Fabric vía ODBC, sin
necesidad de configurar nada manualmente más allá del driver. Toda la
configuración se toma de variables de entorno.

Requisitos previos:
    1. Driver ODBC de SQL Server INSTALADO ("ODBC Driver 17 for SQL
       Server" o "18" — el SQL endpoint de Fabric es compatible con el
       driver estándar, no necesita uno propio).
    2. uv add pyodbc pandas python-dotenv   (ya incluidas en este proyecto)

Variables de entorno necesarias (ponlas en un archivo .env en la raíz del
repo — ver env.example):
    FABRIC_DRIVER    -> nombre exacto del driver instalado (ver instrucciones abajo)
    FABRIC_SERVER    -> endpoint SQL del Warehouse de Fabric
    FABRIC_DATABASE  -> nombre del Warehouse configurado para el producto
    FABRIC_AUTH      -> opcional, default "ActiveDirectoryInteractive"

Cómo obtener el nombre exacto del driver (FABRIC_DRIVER):
    Ejecuta esto en una terminal:

        uv run python -c "import pyodbc; print([d for d in pyodbc.drivers() if 'sql server' in d.lower()])"

    Normalmente aparece como "ODBC Driver 17 for SQL Server" o "18".

Autenticación y caché de sesión:
    Usa Authentication=ActiveDirectoryInteractive. El propio driver ODBC de
    Microsoft (msodbcsql 17.7+/18) cachea el token de Entra ID vía MSAL
    automáticamente: la primera vez abre un login en el navegador, las
    siguientes consultas —aunque sean procesos de Python nuevos— reutilizan
    el token cacheado en silencio hasta que expire. No hace falta código
    adicional para esto.

Uso desde línea de comandos:
    uv run python consultar_fabric.py "SELECT TOP 10 * FROM [<esquema_report>].[nombre_vista]"
    uv run python consultar_fabric.py "SELECT * FROM [<esquema_report>].[nombre_vista]" --output resultado.csv
"""

import argparse
import os
import sys
from datetime import datetime

import pandas as pd
import pyodbc
from dotenv import load_dotenv

from fabric_token_cache import obtener_access_token, token_a_attrs_before

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()  # carga variables desde un archivo .env si existe

# ============================================================
# CONFIGURACIÓN (desde variables de entorno)
# ============================================================
FABRIC_CONFIG = {
    "driver": os.environ["FABRIC_DRIVER"],
    "server": os.environ["FABRIC_SERVER"],
    "database": os.environ["FABRIC_DATABASE"],
    "auth": os.environ.get("FABRIC_AUTH", "ActiveDirectoryInteractive"),
}


def get_connection():
    """Abre una conexión a Fabric.

    Por defecto (FABRIC_AUTH=ActiveDirectoryInteractive, el valor por
    defecto) usa un token de Entra ID obtenido vía MSAL con caché
    persistente en disco (ver fabric_token_cache.py): solo pide login por
    navegador la primera vez; las siguientes conexiones -incluso en
    ejecuciones nuevas del script- son silenciosas. Esto evita el problema
    de que el propio driver ODBC re-pida login en cada conexión nueva.

    Si FABRIC_AUTH tiene cualquier otro valor, se delega la autenticación
    al driver ODBC de forma tradicional (comportamiento anterior).
    """
    conn_str_base = (
        f"DRIVER={{{FABRIC_CONFIG['driver']}}};"
        f"SERVER={FABRIC_CONFIG['server']};"
        f"DATABASE={FABRIC_CONFIG['database']};"
        f"Encrypt=yes;"
    )

    if FABRIC_CONFIG["auth"] == "ActiveDirectoryInteractive":
        token = obtener_access_token()
        return pyodbc.connect(conn_str_base, attrs_before=token_a_attrs_before(token))

    conn_str = conn_str_base + f"Authentication={FABRIC_CONFIG['auth']};"
    return pyodbc.connect(conn_str)


def consultar_vista(schema: str, nombre_vista: str, limite: int = None) -> pd.DataFrame:
    """Consulta una vista de Fabric y devuelve un DataFrame."""
    query = f"SELECT * FROM [{schema}].[{nombre_vista}]"
    if limite:
        query = f"SELECT TOP {limite} * FROM [{schema}].[{nombre_vista}]"  # en T-SQL es TOP, no LIMIT

    with get_connection() as conn:
        df = pd.read_sql(query, conn)
    return df


def consultar_query(query: str) -> pd.DataFrame:
    """Ejecuta cualquier consulta T-SQL personalizada."""
    with get_connection() as conn:
        df = pd.read_sql(query, conn)
    return df


def listar_drivers_sqlserver_instalados() -> list:
    """Utilidad de diagnóstico: lista los drivers de SQL Server detectados por el sistema."""
    return [d for d in pyodbc.drivers() if "sql server" in d.lower()]


def probar_conexion():
    """Utilidad de diagnóstico: valida que la conexión funcione y muestra info básica."""
    try:
        with get_connection():
            print("Conexión exitosa a Fabric.")
            print(f"   Servidor: {FABRIC_CONFIG['server']}")
            print(f"   Warehouse: {FABRIC_CONFIG['database']}")
            print(f"   Autenticación: {FABRIC_CONFIG['auth']}")
    except pyodbc.Error as ex:
        print("Error al conectar a Fabric:")
        print(f"   {ex}")
        print("\nDrivers de SQL Server detectados en este equipo:")
        print(f"   {listar_drivers_sqlserver_instalados()}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Ejecuta una consulta T-SQL contra Microsoft Fabric Warehouse vía ODBC y muestra el resultado."
    )
    parser.add_argument(
        "query",
        help='Consulta T-SQL a ejecutar, ej: "SELECT TOP 10 * FROM [<esquema_report>].[nombre_vista]"',
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Ruta de archivo CSV donde guardar el resultado (opcional).",
    )
    args = parser.parse_args()

    inicio = datetime.now()

    try:
        df = consultar_query(args.query)
    except pyodbc.Error as ex:
        print("Error al ejecutar la consulta contra Fabric:")
        print(f"   {ex}")
        print("\nDrivers de SQL Server detectados en este equipo:")
        print(f"   {listar_drivers_sqlserver_instalados()}")
        sys.exit(1)

    print(f"Filas obtenidas: {len(df)}")
    print(df)

    if args.output:
        df.to_csv(args.output, index=False)
        print(f"Resultado guardado en: {args.output}")

    print(f"Tiempo total: {datetime.now() - inicio}")


if __name__ == "__main__":
    main()
