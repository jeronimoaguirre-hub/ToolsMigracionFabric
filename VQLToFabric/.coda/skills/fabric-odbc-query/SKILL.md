---
name: fabric-odbc-query
description: Consulta Microsoft Fabric Warehouse desde Python vía ODBC en modo lectura, con caché de sesión automático para no repetir el login interactivo en cada consulta. Usar esta skill siempre que el usuario mencione Fabric, Fabric Warehouse, SQL endpoint de Fabric, o pida escribir/depurar un script para consultar objetos, metadatos o datos de Fabric, o diagnosticar errores de conexión ODBC a Fabric.
---

# Consultas a Microsoft Fabric Warehouse vía ODBC

Esta skill permite generar y adaptar scripts en Python para consultar un
Warehouse de Microsoft Fabric a través de ODBC (driver `pyodbc`), usando
variables de entorno para la configuración y autenticación interactiva de
Entra ID con caché automático de token.

Permite consultar el Warehouse de Fabric para revisar objetos, metadatos y
datos autorizados. Úsala siempre en modo de solo lectura dentro de este
harness.

## Cuándo usar esta skill

- El usuario pide un script para consultar/leer vistas de Fabric desde
  Python.
- El usuario reporta errores de conexión ODBC a Fabric (`Login timeout
  expired`, `Cannot open server`, error de autenticación, driver no
  encontrado).
- El usuario pregunta por qué le está pidiendo login otra vez, o cómo
  evitar reautenticarse en cada consulta.

## Archivos incluidos

- `scripts/consultar_fabric.py` — módulo base con las funciones de
  conexión y consulta.
- `scripts/env.example` — plantilla de variables de entorno a copiar como
  `.env` en la raíz del repo.

## Cómo usar esta skill

### 1. Punto de partida

Copia `scripts/consultar_fabric.py` y `scripts/env.example` al proyecto del
usuario (o preséntalos como archivos nuevos si están trabajando en el
chat). No regeneres el script desde cero — parte de esta base y adáptala a
lo que pida el usuario (nombres de vistas, filtros, destino de los datos,
etc.).

**Manejador de paquetes: `uv`, no `pip`.** Este proyecto usa `uv` — instala
dependencias con `uv add <paquete>` (actualiza `pyproject.toml`/`uv.lock`
automáticamente) y ejecuta scripts con `uv run python ...`, nunca `python`
directo ni `pip install`.

El script se ejecuta pasando el SELECT directamente por línea de comandos —
no hace falta editar el archivo para cada consulta:

```bash
uv run python consultar_fabric.py "SELECT TOP 10 * FROM [<esquema_report>].[nombre_vista]"
uv run python consultar_fabric.py "SELECT * FROM [<esquema_report>].[nombre_vista]" --output resultado.csv
```

El resultado se imprime en consola y, si se pasa `--output`/`-o`, también
se guarda como CSV. Si la consulta falla, el script imprime el error y los
drivers de SQL Server detectados en el equipo para ayudar a diagnosticar.

### 2. Requisitos previos que el usuario debe cumplir

Estos requisitos son del entorno del usuario, no algo que Coda pueda
hacer por él — indícaselos claramente:

1. **Driver ODBC de SQL Server instalado** — "ODBC Driver 17 for SQL
   Server" o "18". El SQL endpoint de Fabric es compatible con el driver
   estándar de SQL Server, no necesita uno propio de Microsoft Fabric.
2. **Dependencias del proyecto instaladas**: `uv sync` en la raíz del
   repo (ya incluyen `pyodbc`, `pandas`, `python-dotenv` en
   `pyproject.toml` — no hace falta agregar nada para esta skill).
3. **Variables de entorno** (ver `env.example`):
   - `FABRIC_DRIVER` — nombre EXACTO del driver tal como lo reconoce el
     sistema operativo. Si el usuario no lo sabe, dile que ejecute
     `uv run python -c "import pyodbc; print([d for d in pyodbc.drivers() if 'sql server' in d.lower()])"`,
     o usa la función `listar_drivers_sqlserver_instalados()` incluida en
     el script.
   - `FABRIC_SERVER` — endpoint SQL del Warehouse de Fabric. Ejemplo:
     `xxxxx.datawarehouse.fabric.microsoft.com` (reemplázalo por el endpoint asignado a tu Warehouse).
   - `FABRIC_DATABASE` — nombre del Warehouse configurado para el producto.
   - `FABRIC_AUTH` — opcional, default `ActiveDirectoryInteractive`.

### 3. Autenticación y caché de sesión — no repetir login en cada consulta

El script usa `Authentication=ActiveDirectoryInteractive` en la cadena de
conexión. **El propio driver ODBC de Microsoft (`msodbcsql` 17.7+/18)
cachea el token de Entra ID vía MSAL automáticamente** — la primera vez
abre un login interactivo en el navegador; las siguientes consultas, aunque
sean procesos de Python nuevos, reutilizan el token cacheado en silencio
sin volver a pedir login, hasta que expire (validado empíricamente:
múltiples consultas en procesos separados dentro de la misma sesión de
Windows no repitieron el login).

**No hace falta código adicional para esto** — es el comportamiento por
defecto del driver, no algo que el script implemente. Si en algún momento
sí vuelve a pedir login en cada consulta (por ejemplo, en otra máquina o
tras una política de expiración de sesión distinta), la alternativa es
manejar el caché explícitamente con `azure-identity` +
`TokenCachePersistenceOptions` — pero eso típicamente requiere una app
registrada en Entra ID con acceso a Fabric ya consentida en el tenant; no
lo asumas disponible sin confirmar con el usuario primero, porque intentar
forzarlo puede romper una autenticación que hoy funciona.

### 4. Diagnóstico de errores comunes

| Síntoma | Causa probable |
|---|---|
| `Login timeout expired` / no conecta | VPN caída, o el endpoint de Fabric no es alcanzable desde la red actual |
| Se queda colgado esperando (>1-2 min) | Está esperando que el usuario complete el login interactivo en una ventana del navegador que se abrió — pídele que la revise y la complete |
| `Data source name not found` / driver no encontrado | `FABRIC_DRIVER` no coincide con el nombre exacto instalado |
| Conecta pero la vista no aparece | Nombre de vista/esquema incorrecto, o el usuario no tiene permisos sobre esa vista específica en el Warehouse |
| `Argument data type bigint/int is invalid for argument N of substring/left function` | La columna es numérica (`bigint`/`int`), no texto — hace falta `CAST(columna AS VARCHAR(n))` antes de `SUBSTRING`/`LEFT`. Ver Patrón 17 en `knowledge/patrones-base.md`. |

Si el usuario reporta un error de conexión, sugiere primero correr
`probar_conexion()` del script — imprime el diagnóstico y, si falla, lista
los drivers de SQL Server detectados en el equipo para comparar contra
`FABRIC_DRIVER`.

### 5. Notas de T-SQL (el SQL de Fabric Warehouse)

- Usa `TOP N`, no `LIMIT`, para limitar filas.
- Las vistas de Fabric no aceptan parámetros dinámicos de VQL. Resuelve cada
  `USING PARAMETERS` según su semántica y los patrones P01/P02/P08/P14 de
  `knowledge/patrones-base.md`; no inventes un filtro ni valores de parámetro.
- Cuidado con columnas que parecen fecha pero son `bigint`/`int` en formato
  `YYYYMMDD`, y con el indexado de `SUBSTRING`/`LEFT` — ver P17/P28.

## Seguridad

- Nunca hardcodees el endpoint ni credenciales en el script — siempre por
  variable de entorno o `.env` (y recuerda que `.env` no debe subirse a
  control de versiones).
- El caché de token de MSAL vive fuera del repo (perfil de usuario de
  Windows) — no es algo que este proyecto gestione ni deba versionar.
