# Instrucciones para CODA — Documentación de transición TRS - 9

Este documento le dice a CODA **qué entregar, en qué orden y con qué herramientas** para dejar lista la documentación de transición de un producto de datos en Microsoft Fabric. Léelo completo antes de actuar y síguelo por fases. Si algo no está aquí, pregunta; no improvises.

## 0. Qué se entrega

Para cada producto/workspace se generan **3 artefactos** a partir de las plantillas de esta carpeta (`TRS - 9/`):

| # | Plantilla | Se genera | Cuántas veces |
|---|-----------|-----------|---------------|
| 1 | `Inventario_Fabric_WS_XXX.template.xlsx` | `Inventario_Fabric_<Producto>.xlsx` | 1 por producto (cubre Silver y Gold) |
| 2 | `TRS - 9. APROPIACIÓN TÉCNICA DEL SERVICIO.template.md` (**página padre**) | `TRS-9 Padre - <Producto>.md` | 1 por producto |
| 3 | `APROPIACIÓN TÉCNICA DEL SERVICIO (Release XX).template.md` (**página hija**) | `TRS-9 Hija (Release <NN>) - <Producto>.md` | 1 **por cada Release o Evolutivo** |

- **Padre**: información general del desarrollo (ambientes y registro de capacitaciones). Su última fila de la tabla de capacitación (`Apropiación técnica Release XXXX`) apunta a la página hija del release.
- **Hija**: detalle técnico del release (ambientes con roles, conexiones, archivos, modelo, arquitectura, pipelines, inventario, capacitación).
- **Inventario .xlsx**: es el adjunto que referencia la sección "Inventario Objetos" de la página hija.

**Nombres de archivo locales** (fijos, para no confundir padre e hija): `TRS-9 Padre - <Producto>.md`, `TRS-9 Hija (Release <NN>) - <Producto>.md` e `Inventario_Fabric_<Producto>.xlsx`. El **título de la página en la wiki** es otra cosa: la padre conserva el nombre de la página existente en la wiki (si no existe, `TRS-9 <Producto>`) y la hija se titula `APROPIACIÓN TÉCNICA DEL SERVICIO (Release <NN>) - <Producto>`.

`<Producto>` es el nombre del producto que da el usuario (p. ej. `DMProyectos`). El título `#` de cada página es `<Producto>` seguido de los workspaces entre paréntesis (`DMProyectos (WS-Silver / WS-Gold)`).

Los archivos generados se guardan en la raíz de `TransicionAgent/`. **Nunca modifiques las plantillas `.template.*`**; copia y llena la copia.

**Fuera de alcance:** el **Modelo de Datos** (`ModeladoDeDatos.xlsx`) NO se llena en la transición: se diligencia desde el inicio del producto y debe existir antes. En la página hija, sección "Modelo de Datos", solo registra el link que dé el usuario (o deja `<DATO REQUERIDO: URL DEL MODELO DE DATOS>`); no generes ese Excel.

**Ambientes y nombres de workspace.** Cada producto tiene sus workspaces repartidos en **tres ambientes**: DEV, QA y PRD. El usuario da el de **DEV** (cuyo nombre varía: `WS-FB-DEV-<Nombre>-<Sufijo>`, p. ej. `WS-FB-DEV-ProyectosOperativos-GLB`, o `WS-FB-DEV-<Otro>`). Los de QA y PRD **solo cambian el ambiente** en el nombre: `WS-FB-QA-<Nombre>…` y `WS-FB-PRD-<Nombre>…` (p. ej. `WS-FB-DEV-DMProyectosGold` → `WS-FB-QA-DMProyectosGold` → `WS-FB-PRD-DMProyectosGold`). Aplica a cada capa (Silver, Gold). De ahí:
- **QA**: deriva el nombre cambiando `DEV` por `QA` y búscalo en Fabric (`fab ls` / `GET /workspaces`). Normalmente **sí es visible**: toma de ahí nombre, `URL` e `IDWorkspace`. Si no hay coincidencia exacta (a veces cambia el sufijo, p. ej. `…-GLB`), lista los parecidos; no elijas en silencio (en modo no interactivo usa solo el candidato evidente y dilo en el reporte).
- **PRD**: deriva el nombre cambiando `DEV` por `PRD`, pero **no lo busques ni insistas**: en PRD ningún usuario tiene permisos, así que no será visible. Escribe el nombre derivado marcado como **inferido** (p. ej. `WS-FB-PRD-X (inferido, no verificado)`) y deja `URL` e `IDWorkspace` como `<DATO REQUERIDO: URL WORKSPACE>` / `<DATO REQUERIDO: IDWORKSPACE>` para que los entregue el usuario u Operaciones. No inventes la URL ni el ID.
- La **información técnica** (inventario, pipelines, conexiones, tablas) se recolecta **del workspace de DEV** que dio el usuario; los workspaces de QA (visible) y PRD (no visible) se usan **solo para las filas de Ambientes** (§6.2/§6.3 sección 1). No inventaríes sus objetos salvo que el usuario lo pida.
- Otros workspaces "hermanos" que no sean el QA/PRD del mismo producto (otro dominio u otro producto): **no los incluyas**; menciónalos en el reporte final y deja que el usuario decida.

**Alcance de workspaces:** documenta **solo los workspaces que el usuario nombró** (p. ej. un Silver y un Gold de DEV) más sus equivalentes de QA/PRD para la tabla de Ambientes. En el Excel del Inventario la columna `Ambiente` conserva el rótulo `DEV/QA` (los objetos inventariados son los de DEV, que se promueven a QA); en las tablas de Ambientes del TRS-9 se usan filas `DEV`, `QA` y `PRD`.

**Capa (Bronze/Silver/Gold):** se asigna **por objeto**, por el prefijo del nombre (`brz`, `slv`, `gld`); si no tiene prefijo, se usa la capa del workspace que dio el usuario. Un `lh_brz_*` dentro del workspace Silver es Bronze.

Cuando el usuario diga "llena la documentación" sin más, haz las fases 1 → 5 en orden. Si pide solo una pieza (p. ej. "solo el inventario"), haz las fases 1–3 y la pieza pedida.

## 1. Reglas generales (aplican siempre)

1. **Solo lectura sobre Fabric.** Nunca crees, modifiques ni borres items, conexiones, roles ni datos. Las skills REST ya bloquean PUT/PATCH/DELETE; respeta ese espíritu con `fab` y el MCP (solo `ls`, `get`, `GET`, `SELECT`).
2. **No inventes datos.** Si un dato no se puede obtener con las herramientas ni lo dio el usuario, deja la etiqueta de la plantilla intacta: `<DATO REQUERIDO: ...>`. Al terminar, lista todo lo que quedó pendiente (ver §8).
3. **Nunca imprimas ni copies secretos.** No muestres el contenido de `.env`, tokens ni contraseñas. Para verificar el `.env`, comprueba solo que las claves existan (nombres, no valores).
4. **`uv`, no `pip` directo, para dependencias del proyecto.** Instala con `uv add <paquete>` y ejecuta con `uv run python ...`. (`pip` solo se usa para instalar la CLI `fab` si no hay `uv`.)
5. **Pregunta antes de publicar.** Subir páginas a la wiki de Azure DevOps (`DemocratizacionDeDatos.wiki`, org `ecopetrolad`) requiere permiso explícito del usuario, indicando nombre y contenido de cada página. Las rutas reales usan espacios (p. ej. `/Producto de Datos/ProyectosPD/Apropiación`) aunque la URL muestre guiones; verifica con `wiki get_page` antes de crear ancestros.
6. **Formato.** Idioma español. Fechas `DD-MM-AAAA` en tablas de capacitación (como pide la plantilla); en el resto `AAAA-MM-DD` es aceptable si es consistente en el documento. Duraciones en `X min` / `X segundos`. Conserva `[[_TOC_]]` y la estructura de títulos de la plantilla.
7. **Tablas con varias filas.** Las plantillas traen **una sola fila de ejemplo** por tabla que solo indica qué dato va en cada columna. Si hay más de un ítem (varias conexiones, pipelines, objetos, capacitaciones...), **agrega una fila por ítem** y elimina la fila-plantilla cuando ya esté llena.
8. **Encoding.** En Windows ejecuta Python con `PYTHONIOENCODING=utf-8` (o `sys.stdout.reconfigure(encoding="utf-8")`) y guarda los `.md` en UTF-8.
9. **No improvises lo que ya tiene script.** Para inventario usa la skill `fabric-inventory` (§5); para roles, conexiones y pipelines usa las skills del §6.1. Escribir decenas de `python -c` sueltos es lo que más tiempo consume y deja errores. Si un script falla, repórtalo y corrígelo en la skill; no lo rodees.
10. **Prioriza entregables.** Genera los archivos finales (xlsx y .md) en cuanto tengas los datos; después refínalos. Un borrador completo con pendientes marcados vale más que una recolección exhaustiva sin documento.
11. **Presupuesto de tiempo.** Toda la corrida (preflight → documentos → plan de publicación) debe caber en ~20 minutos. El inventario y las conexiones son un comando cada uno; el plan de publicación no debe pasar de ~8 llamadas al MCP de wiki. Si algo se atasca, deja la etiqueta, anótalo y continúa.
12. **Anti-bucle.** Si repites el mismo tipo de consulta 3 veces sin obtener un dato nuevo, **detente**: deja la etiqueta, anótalo en el reporte y sigue con el siguiente paso. Consulta solo datos que alguna plantilla pide. Usa **exactamente** los scripts y argumentos de la receta del §6.0; no adivines nombres de script (no existen `pipelines_ops.py`, `roles_workspace.py`, etc.) ni de módulos.
13. **Scripts temporales** van en `.coda/tmp/` (ignorada por git). Pueden servir de ejemplo, pero **revísalos antes de reutilizarlos** (los de corridas anteriores pueden tener errores; los scripts confiables están en `.coda/skills/*/scripts/`).

## 2. Fase 1 — Verificar herramientas instaladas (preflight)

**Un solo comando** hace todas las comprobaciones (herramientas, sesiones, dependencias Python, ODBC y `.env`) y, con `--instalar`, instala lo que se puede sin tocar el sistema (`uv sync` y `fab`):

```bash
python .coda/skills/trs9-preflight/scripts/preflight.py            # verifica (tarda ~1 min por `az`)
python .coda/skills/trs9-preflight/scripts/preflight.py --instalar # verifica + instala dependencias Python y fab
```

Ejecútalo **antes de preguntar o recolectar nada**, muestra su tabla al usuario y resuelve lo marcado `FALTA` (lo de sistema —Python, uv, Azure CLI, Node.js, ODBC, .NET— lo instala el usuario; dile el paso exacto; `az login` y `fab auth login` también los hace el usuario, abren el navegador). Si `--instalar` hace falta, **pide confirmación** antes de ejecutarlo. La tabla siguiente es la referencia de qué se usa para qué:

| Herramienta | Para qué se usa | Comprobar | Si falta |
|---|---|---|---|
| **Python 3.10–3.13** | Todos los scripts | `python --version` | Usuario: instalar Python |
| **pip** | Instalar `fab` | `pip --version` | Viene con Python |
| **uv** | Dependencias y ejecución de scripts | `uv --version` | `pip install uv` |
| **fabric-cli (`fab`)** | Explorar workspaces, items, carpetas, tablas | `fab --version` | `uv tool install ms-fabric-cli` (o `pip install ms-fabric-cli`) y luego `fab auth login` |
| **Driver ODBC de SQL Server (17 o 18)** | Consultar SQL endpoint de Lakehouse/Warehouse (skill `fabric-odbc-query`) | PowerShell: `Get-OdbcDriver \| ? Name -like '*SQL Server*'` | **Usuario**: instalar "ODBC Driver 18 for SQL Server" |
| **Azure CLI (`az`)** | Autenticación de las skills REST (`AzureCliCredential`) y del MCP de Fabric | `az --version` y `az account show` | **Usuario**: instalar; luego `az login` (tenant ECP) |
| **npm / npx (Node)** | Lanzar el MCP de Azure DevOps (`npx @azure-devops/mcp`) | `npm --version` | **Usuario**: instalar Node.js LTS |
| **dnx (.NET 10 SDK)** | Lanzar el MCP de Fabric (`dnx Microsoft.Fabric.Mcp`) | `dnx --help` | **Usuario**: instalar .NET 10 SDK |

Notas:
- Lo que dice "Usuario" son instalaciones de sistema: indícaselas, no las intentes por tu cuenta. `uv`, `fab` y paquetes Python sí puedes instalarlos tú (pide confirmación antes).
- El **nombre exacto del driver ODBC** instalado es el que va en `FABRIC_DRIVER`. `env.example` trae "17" de ejemplo; si en el equipo solo está el 18, usa `ODBC Driver 18 for SQL Server`.
- Verifica sesiones: `az account show` (debe mostrar el tenant de Ecopetrol; si no, pide `az login`) y `fab auth status` (si no hay sesión, pide `fab auth login`).
- **Permisos**: `.coda/config.json` ya autoriza (sin preguntar) los comandos de preflight, `uv init --bare`/`uv add`/`uv sync`, `uv run python`, `uv tool install ms-fabric-cli` y lectura con `fab`/`az`. Lo demás pide aprobación; en modo no interactivo (`coda -p`) lo que requiera aprobación se rechaza: repórtalo en vez de reintentarlo. `az login` está deliberadamente en `deny`: si la sesión no está activa, pídele al usuario que la inicie.
- Un primer `az` o `fab` puede tardar ~8 s en dar el token; es normal, no lo trates como fallo. No lances `az account get-access-token` repetidamente: el cliente REST de las skills ya cachea el token.
- El MCP de Fabric y el de Azure DevOps se declaran en `.coda/mcp.json` (credencial del MCP de Fabric: `AzureCliCredential`, por eso `az login` es obligatorio). Si sus herramientas no aparecen disponibles, díselo al usuario en vez de asumir que existen.

## 3. Fase 2 — Preguntar al usuario los datos del producto

Haz **una sola ronda de preguntas**, solo por lo que falte; no preguntes lo que ya dijo el usuario o puedas deducir.

**Obligatorio:**
1. **Nombre del workspace** (Bronze/Silver donde vive el desarrollo). Debe coincidir **exacto**; si el nombre que dio el usuario no existe, el script de recolección lista los parecidos y se detiene: confirma con el usuario (en modo no interactivo, usa el único candidato evidente, dilo explícitamente en el reporte y continúa).
2. **Nombre del Lakehouse Silver** dentro de ese workspace (si el usuario no lo da, se descubre listando los items `Lakehouse` del workspace; confírmalo si hay más de uno con prefijo `slv`).
3. **Número de Release / Evolutivo** que se documenta (define la página hija) y **nombre del producto** (se usa en los nombres de archivo y en el título).
4. **Ambiente(s)**: basta con el nombre del workspace de **DEV**; el de QA y el de PRD se derivan de él (ver §0, "Ambientes y nombres de workspace"). Pregunta solo si el usuario indica que el nombre de QA o PRD **no sigue** esa convención.

5. **Destino en la wiki de Azure DevOps**: carpeta del equipo de producto de datos donde viven las páginas de apropiación (patrón en este tenant: `/Producto de Datos/<EquipoPD>/Apropiación`, p. ej. `ProyectosPD`). Si el usuario no la sabe, propón candidatos tras buscar en la wiki (§8.4).

**Solo si el producto incluye capa Gold (pregúntalo):**
6. Nombre del **workspace Gold**, y el nombre de su **Lakehouse o Warehouse** Gold.

**Datos organizacionales (no están en Fabric; pídelos, o déjalos como `<DATO REQUERIDO>` si el usuario no los tiene):**
- Líder funcional y Responsable del dominio.
- Responsable(s) de las conexiones/fuentes.
- Capacitaciones realizadas: fecha, link de video/manual, responsable.
- Links del modelo de datos y de los diagramas de arquitectura/ER.

### Archivo `.env` (credenciales/configuración ODBC)

Ubicación usada por la skill: `.coda/skills/fabric-odbc-query/scripts/.env` (plantilla: `env.example` en la misma carpeta). Debe tener estas claves:

| Clave | Valor |
|---|---|
| `FABRIC_DRIVER` | Nombre **exacto** del driver instalado (ver §2) |
| `FABRIC_SERVER` | Cadena de conexión del **SQL endpoint** (`xxxx.datawarehouse.fabric.microsoft.com`). Se obtiene con `GET /v1/workspaces/{ws}/lakehouses/{lh}` → `properties.sqlEndpointProperties.connectionString` (o en el portal: SQL endpoint → Copy SQL connection string) |
| `FABRIC_DATABASE` | Nombre del Lakehouse/Warehouse a consultar (Silver, o Gold si se consulta Gold) |
| `FABRIC_AUTH` | Opcional; default `ActiveDirectoryInteractive` (primer login en navegador, luego token cacheado) |

Reglas:
- Verifica que exista y tenga las 3 claves obligatorias **sin mostrar valores**. Si falta o está incompleto, ofrece generarlo a partir de `env.example` con los datos que dio el usuario (el servidor lo puedes resolver tú con `fab`/API) y confirma antes de escribirlo.
- `.env` está en `.gitignore`; nunca lo imprimas ni lo muestres en el resumen final.
- Si hay que consultar **Silver y Gold** (dos bases distintas), el `.env` solo apunta a una a la vez: cambia `FABRIC_SERVER`/`FABRIC_DATABASE` entre consultas, o pásalos como variables de entorno del proceso, y avisa al usuario.

## 4. Fase 3 — Dependencias de los scripts de las skills

Los scripts de `.coda/skills/*/scripts/` necesitan estos paquetes: `pyodbc`, `pandas`, `python-dotenv`, `msal` (ODBC con token cacheado), `azure-identity`, `requests` (skills REST), `openpyxl` (llenar el .xlsx) y `pyyaml` (leer `ArchivoConfiguracion/*.yml`).

1. Si **no existe `pyproject.toml`** en `TransicionAgent/` (hoy no existe): `uv init --bare` y luego
   `uv add pyodbc pandas python-dotenv msal azure-identity requests openpyxl pyyaml`.
2. Si existe: `uv sync`.
3. Verifica: `uv run python -c "import pyodbc, pandas, dotenv, msal, azure.identity, requests, openpyxl, yaml; print('ok')"`.
4. Prueba la conexión SQL con `probar_conexion()` de `consultar_fabric.py` (ver skill `fabric-odbc-query`) **solo si se va a consultar SQL**; el primer intento abre un login en el navegador: avísale al usuario antes.

Los scripts se ejecutan **desde la raíz de `TransicionAgent/`**:
`uv run python .coda/skills/<skill>/scripts/<script>.py <args>`

## 5. Fase 4 — Llenar el Inventario Fabric (`Inventario_Fabric_WS_XXX.template.xlsx`)

Se hace con la skill **`fabric-inventory`** (ver su `SKILL.md`): dos comandos, ~1 minuto. Hoja única de la plantilla: **`Lista de objetos`**.

```bash
# 1) Recolectar (solo lectura): items + rutas de carpeta + tablas por esquema + schedules/duración de pipelines
uv run python .coda/skills/fabric-inventory/scripts/recolectar_workspace.py \
  --workspace "Silver=<WS Silver>" [--workspace "Gold=<WS Gold>"] \
  --output .coda/tmp/inventario-datos.json

# 2) Llenar el xlsx
uv run python .coda/skills/fabric-inventory/scripts/llenar_inventario.py \
  --datos .coda/tmp/inventario-datos.json \
  --salida Inventario_Fabric_<Producto>.xlsx \
  --nombre-workspace "<WS Silver> / <WS Gold>" \
  --ambiente DEV/QA --estado Nuevo [--responsable "<Responsable del dominio>"]
```

Sobre el resultado:
- **11 columnas** en este orden: Ambiente, Capa, Nombre de Carpeta, Subcarpeta, Nombre, Tipo de Objeto, Estado (nuevo/actualizado), Descripción, Frecuencia de actualización, Duración promedio (QA), Duración promedio (QA). `D1` = nombre(s) del workspace, `D2` = responsable del dominio (del usuario; si no lo da queda la etiqueta).
- **Carpeta / Subcarpeta**: ruta real del item en Fabric; la última carpeta es la Subcarpeta y el resto el Nombre de Carpeta (como el ejemplo de la plantilla: `Ingesta/Valnav` + `Notebooks`). Tablas Delta: carpeta `<lakehouse>/Tables`, subcarpeta = esquema.
- **Estado**: `Nuevo` por defecto en un primer release; `Actualizado` si el usuario lo indica.
- **Descripciones**: las toma de Fabric; las que falten quedan como `<DATO REQUERIDO: DESCRIPCION>`. Cuando puedas redactar una descripción **fiel** (leyendo la definición del notebook/pipeline), escribe un JSON `{"nombre": "descripción"}` y pásalo con `--descripciones`. No uses frases genéricas de relleno ni inventes.
- **Warehouse Gold**: sus tablas/vistas no salen por API (el JSON trae un aviso). Si el usuario las quiere en el inventario, consúltalas con `fabric-odbc-query` (`INFORMATION_SCHEMA.TABLES`; requiere login interactivo en navegador, avísale) o déjalo anotado como pendiente.
- La duración aparece duplicada (el encabezado de la plantilla repite "(QA)"): el script repite el valor y debes mencionarlo en el reporte.
- El script ya valida los encabezados, relee el archivo y reporta filas/columnas y pendientes; no hace falta otro verificador.

## 6. Fase 5 — Llenar las plantillas TRS - 9 (padre e hija)

Parte de la plantilla, reemplaza cada `<DATO REQUERIDO: ...>` por el dato real y deja la etiqueta si no lo tienes. Orden recomendado: recolectar todo (6.1) → llenar hija (6.2) → llenar padre (6.3).

### 6.0 Receta de comandos (copiar tal cual, desde la raíz de `TransicionAgent/`)

```bash
# A. Inventario + pipelines (schedules, duración, runs) + tablas  -> .coda/tmp/inventario-datos.json
uv run python .coda/skills/fabric-inventory/scripts/recolectar_workspace.py --workspace "Silver=<WS Silver>" --workspace "Gold=<WS Gold>" --output .coda/tmp/inventario-datos.json
# B. Excel del Inventario
uv run python .coda/skills/fabric-inventory/scripts/llenar_inventario.py --datos .coda/tmp/inventario-datos.json --salida Inventario_Fabric_<Producto>.xlsx --nombre-workspace "<WS Silver> / <WS Gold>" --ambiente DEV/QA --estado Nuevo
# C. Conexiones realmente usadas (credencial, host/BD, gateway y su estado) -> .coda/tmp/conexiones-usadas.json
uv run python .coda/skills/fabric-connections-audit/scripts/conexiones_workspace.py --workspace "<WS Silver>" --workspace "<WS Gold>" --con-gateways --output .coda/tmp/conexiones-usadas.json
# D. Roles (uno por workspace; 403 = Viewer -> dejar pendiente y seguir)
uv run python .coda/skills/fabric-workspace-access/scripts/consultar_acceso_workspace.py --workspace <idWS> --solo-roles
```

**Estructura de `inventario-datos.json`** (léela directamente, no la explores con scripts): `workspaces[]` con `nombre`, `id`, `url`, `capa_defecto`, `items[]` (`id`, `tipo`, `nombre`, `descripcion`, `carpeta`, `capa`), `pipelines{<itemId>: {schedules[]{activo,texto}, runs{total_runs, duracion_promedio_min, duracion_p95_min, tasa_fallo_pct, scheduled, manual, ultimo_error}}}`, `tablas{<lakehouseId>: {esquema: [tablas]}}` y `avisos[]`. **Las secciones 6 (Pipelines), 7 (Inventario) y 3 (Tipo de Archivos) de la página hija salen de este JSON**; no vuelvas a consultar la API por pipelines.
**Estructura de `conexiones-usadas.json`**: `conexiones[]` con `nombre`, `connectivityType`, `credentialType`, `tipo`, `path`, `gateway`, `gatewayStatus`, `ultimoUsoCredencial`, `pipelines[]`; y `errores[]`.

Orden sugerido: A → B → C → D (y `fab`/MCP solo para dudas puntuales) → escribir primero la **página hija**, luego la **padre** → plan de publicación.

### 6.1 Cómo obtener cada dato

| Dato | Herramienta | Detalle |
|---|---|---|
| Inventario de items, carpetas, tablas, schedules y duración de pipelines | Skill **`fabric-inventory`** (§5) | Un solo JSON reutilizable también para las secciones 6 y 7 de la página hija |
| Exploración puntual de workspaces/items/carpetas | `fab` o MCP de Fabric | `fab ls`, `fab get`, `fab api`; URL del workspace: `https://app.fabric.microsoft.com/groups/<workspaceId>` |
| **Roles asignados** (Admin/Member/Contributor/Viewer) | Skill **`fabric-workspace-access`** con `--solo-roles` (la capacidad/SKU **no** es un campo de ninguna plantilla: no la consultes) | Requiere rol Member+ en el workspace. Si responde **403 (`InsufficientWorkspaceRole`)** el usuario es Viewer: no insistas ni busques rodeos; deja `<DATO REQUERIDO: ROLES ASIGNADOS>` y anótalo en pendientes (de quién: un Admin/Member del workspace o el portal). Los grupos aparecen sin expandir miembros |
| **Conexiones que usa el workspace** (tipo de credencial, conectividad, host/BD, gateway y su estado, pipelines que la usan) | Skill **`fabric-connections-audit`** → `conexiones_workspace.py --workspace <WS> [--workspace <WS2>] --con-gateways --output .coda/tmp/conexiones-usadas.json` | **Un solo comando** hace el cruce pipeline→conexión→datos. Lista únicamente las conexiones realmente usadas, no todas las del tenant. `auditar_conexiones.py` queda solo para auditorías generales del tenant |
| Host / servidor / BD de la fuente | Campos `tipo` y `path` de `conexiones-usadas.json` (vienen de `connectionDetails`) | `path` trae `servidor;base`, `host:puerto` o la URL; úsalo para `HostName/IP` e `Instancia/Nombre BD` antes de dejar la etiqueta |
| **Schedules, frecuencia, duración promedio, tasa de fallo, último error** | Skill **`fabric-pipeline-ops`** | Duración = promedio de `endTimeUtc − startTimeUtc` sobre ~100 runs recientes |
| Tablas, columnas y tipos del Lakehouse/Warehouse | `fab`, API `.../lakehouses/{lh}/tables`, o skill **`fabric-odbc-query`** (`INFORMATION_SCHEMA`) | Solo `SELECT`, T-SQL (`TOP N`, no `LIMIT`) |
| Archivos de configuración de ingesta (fuentes, vistas, ventanas) | `ArchivoConfiguracion/*.yml` | Útil para descripciones de fuentes y frecuencia de extracción |
| Wiki / repos / work items de Azure DevOps | MCP `azure-devops` | Lectura. Escritura en wiki solo con permiso (regla 5) |
| Líder, responsables, capacitaciones, links | **El usuario** | No existen en Fabric |

Nota para llamadas REST propias con `FabricRestClient`: las rutas son **relativas a la base** (`/connections`, `/workspaces/{id}/items`), sin el prefijo `/v1` (con él da 404). Un gateway que no aparece en `GET /gateways` (404) no es visible para este usuario: deja el nombre como pendiente de portal.

Detalle de herramientas y límites: ver `.coda/skills/*/SKILL.md` y `.coda/tmp/fabric-api-research.md`. Throttling: ante HTTP 429 el cliente reintenta con `Retry-After`; no lances barridos masivos en paralelo.

### 6.2 Página hija — `APROPIACIÓN TÉCNICA DEL SERVICIO (Release XX)` (8 secciones)

Título (`#`): `<Producto> (<WS Silver> / <WS Gold>)`. Respeta la estructura de la plantilla: no agregues elementos que no traiga (p. ej. `[[_TOC_]]` solo está en la padre).

1. **Ambientes** — una fila por **ambiente y workspace**: `DEV`, `QA` y `PRD` (la plantilla trae filas `DEVQA` y `PRD`; desdobla `DEVQA` en `DEV` y `QA`). Nombres, URL e ID según §0 "Ambientes y nombres de workspace": DEV y QA con datos reales; PRD con el nombre inferido y `URL`/`IDWorkspace` como etiqueta. Si el producto tiene Silver y Gold, una fila por **workspace** de cada ambiente (capa distinta). `Capa`: Bronze/Silver/Gold (se deduce de los lakehouses/prefijos `brz/slv/gld` y de lo que diga el usuario). `URL` e `IDWorkspace` desde Fabric. `Roles asignados`: formato compacto `Admin: a@..., b@...; Member: ...; Contributor: ...; Viewer: ...` (grupos como `Grupo <nombre>`). Líder funcional y Responsable del dominio: del usuario. `Roles asignados` de QA/PRD: de QA solo si tienes Member+; de PRD, etiqueta. **Formato con Silver + Gold:** primero las filas de `DEV` (una por capa), luego las de `QA` y al final las de `PRD`, con `Capa` distinta en cada una.
2. **Fuentes de Datos y Conexiones** — una fila por conexión **usada por el workspace**.
   - `Nombre de la Fuente`: sistema legible (p. ej. "SAP HANA", "Azure DevOps").
   - `Ambiente`: DEV/QA/PRD (se deduce del sufijo/nombre de la conexión y de dónde la usan los pipelines; si es ambiguo, pregunta).
   - `Metodo de autenticacion`: `credentialType` (Basic, OAuth2, ServicePrincipal, Key, Windows...).
   - `Nombre de Conexión`: `displayName`. `Tipo de Conexión`: `connectivityType` (OnPremisesGateway, ShareableCloud, VirtualNetworkGateway...).
   - `HostName/Ip`, `Instancia/Nombre BD`: de `connectionDetails.path`.
   - `Nombre Gateway`: nombre del gateway (si es cloud, `(gateway virtual)`/`No aplica`); incluye estado Online/Offline en `Observación` si corriste `--con-gateways`.
   - `Fecha Vencimiento credenciales`: **no disponible por API** → deja `<DATO REQUERIDO: verificar en portal>` y agrega al pie de la tabla el aviso: *el vencimiento de credenciales no está disponible por API; verificar en el portal de Fabric (Manage connections and gateways). Señal indirecta: rol `PendingOwner` indica renovación pendiente.* Puedes citar `lastCredentialUsedDateTime` en Observación.
   - `Responsable`: del usuario. `Imagen`: captura del usuario (déjalo como etiqueta).
3. **Tipo de Archivos** — **solo con lo que está en el JSON, sin inferir ubicaciones**: (a) por cada lakehouse y esquema de `tablas`, una fila `Delta` con `Ubicación` = `/<lakehouse>/Tables/<esquema>/`, el nº de tablas en `Nombre Archivo`; (b) por cada carpeta de primer/segundo nivel de `archivos` (p. ej. `Files/Ecopetrol/SAP/...`), una fila con su tipo (Parquet/JSON/YAML según el contenido o la carpeta; si no se sabe, `<DATO REQUERIDO: TIPO DE ARCHIVO>`). `Repositorio` = `OneLake`. **No pongas tablas en un lakehouse distinto al que el JSON indica** (p. ej. las tablas Delta de negocio están en el lakehouse Silver, no en el Bronze) ni rutas de `Files/` que no aparezcan en `archivos`. `Particionamiento`: etiqueta si no lo puedes leer. `Conexión o Usuario`/`Nombre Conexión`: la conexión de `conexiones-usadas.json` que alimenta esa ruta si es evidente por el nombre de la carpeta/pipeline; si no, etiqueta.
4. **Modelo de Datos** — **no se llena aquí** (ver §0): deja el link del usuario o la etiqueta. Tabla de versiones: `Versión` (1.0 en el primer release), `Nombre` (lakehouse/modelo), `Editable`, `Dependencias` (lakehouses/pipelines/fuentes de las que depende), `Fecha` (hoy), `Observación` (conteo de objetos por tipo).
5. **Arquitectura** — primera tabla: workspace + links de diagrama de arquitectura y ER (del usuario). Segunda tabla: versiones entregadas a Operaciones (`Versión`, `Nombre`, `Editable`, `Fecha`, `Observación`).
6. **Pipeline Historicos e Incrementales** — una fila **por pipeline** (skill `fabric-pipeline-ops`): `Versión`, `Nombre`, `Editable` (Sí/No), `Fecha`, `Observación` (nº de schedules activos/deshabilitados, nº de runs, tasa de fallo si es relevante), `Frecuencia extraccion y ejecución` (texto legible con zona horaria y si está **ACTIVO** o *disabled*; `Sin schedule` / `Manual` si no hay), `Duracion Promedio carga/Volumen Prom datos` (`X min (N runs)`; `-` si no hay runs). Distingue pipelines históricos (carga completa/one-time) de incrementales (ventana/delta) cuando el nombre o la definición lo permita. **Convenciones:** `Versión` = número de release documentado (p. ej. `1`); `Fecha` = fecha de la documentación (Fabric no expone versión ni fecha de creación por pipeline). **Histórico vs incremental**: clasifica solo si el nombre o la descripción lo dicen (`delta`, `window`, `incremental` → incremental; `one_time`, `full`, `historico` → histórico); si no, no clasifiques. Si un pipeline aparece en dos carpetas de Fabric, repórtalo una sola vez.
7. **Inventario Objetos** — misma información del Excel (§5), una fila por objeto relevante, columnas: Ambiente, Capa, Nombre de Carpeta, Subcarpeta, Nombre, Tipo de Objeto, Descripción, Frecuencia, Duración. Mantén el enlace `Editable Plantilla Base` y recuerda al usuario adjuntar el `.xlsx` generado a la wiki. **Qué filas van en la página** (el detalle completo vive en el `.xlsx`, nunca 300 filas aquí): una fila por Lakehouse, Warehouse, SQL endpoint, Environment, VariableLibrary y **DataPipeline**; los **notebooks** y las **tablas Delta** se resumen en **una fila por carpeta/esquema** con el conteo (`N notebooks`, `N tablas`); los reportes/modelos semánticos se resumen en una fila por tipo con conteo. Indica siempre al inicio de la sección que el detalle completo está en el adjunto.
8. **Capacitación funcional y técnica** — filas con `Fecha DD-MM-AAAA`, `Versión`, `Documentos`, `Evidencia`, `Descripción`: solo con lo que dé el usuario.

### 6.3 Página padre — `TRS - 9. APROPIACIÓN TÉCNICA DEL SERVICIO` (2 secciones)

1. **Ambientes** — igual que la sección 1 de la hija (filas `DEV`, `QA`, `PRD`) pero **sin** las columnas `Roles asignados` ni `IDWorkspace` (la padre tiene 6 columnas).
2. **Capacitación funcional y técnica** — filas: sesión técnica, sesión funcional, manual funcional (si aplica), manual técnico (si aplica) y **una fila `Apropiación técnica Release XXXX` por cada release**, cuyo `Evidencia` es el link a la página hija de ese release y `MVP o Release` su número. Todo dato (fecha, link, responsable) viene del usuario.

## 7. Cómo trabajar con las herramientas (guía de decisión)

- **Primero `fab`/MCP de Fabric** para descubrir: workspaces, items, carpetas, tablas. Son rápidos y cubren casi todo el inventario.
- **Skills REST** (`fabric-workspace-access`, `fabric-connections-audit`, `fabric-pipeline-ops`, cliente común `fabric-rest-api`) para lo que `fab`/MCP **no** exponen: roles, conexiones, gateways, schedules e historial de runs. Requieren `az login`.
- **`fabric-odbc-query`** para metadatos/datos por SQL (tablas, columnas, conteos) en el SQL endpoint del Lakehouse o Warehouse Gold. Solo `SELECT`.
- **MCP Azure DevOps** para wiki/repos/work items.
- Si una herramienta falla por permisos (403) o no está disponible: **dilo**, usa la alternativa si existe (p. ej. API en lugar de `fab`), y si no, deja la etiqueta. No fabriques el dato.
- Skills REST: el `jobType` de schedules se prueba como `Pipeline` y luego `DefaultJob`; el historial son ~100 runs recientes; `/connections` solo devuelve lo que el usuario puede ver; un usuario Viewer no puede leer roles. Comunica estas limitaciones cuando afecten el resultado.

## 8. Cierre: verificación y reporte

Antes de dar por terminado:
1. Busca `<DATO REQUERIDO` en los `.md` generados y en el `.xlsx`; entrega al usuario una **lista agrupada por sección** de lo pendiente y **de quién** depende (usuario, portal de Fabric, otro equipo).
2. Verifica que no queden filas-plantilla vacías duplicadas, que las tablas conserven sus encabezados y que el `.xlsx` tenga 11 columnas alineadas.
3. Resume qué se llenó automáticamente y con qué fuente (Fabric/API/ODBC), y qué supuestos hiciste (p. ej. ambiente deducido, capa deducida, columna K repetida).
4. **Plan de publicación** (solo lectura con el MCP `azure-devops`, wiki `DemocratizacionDeDatos.wiki`; máximo ~8 llamadas). Identifica los **candidatos** de destino: (a) la carpeta con el **nombre exacto del producto** (`get_page` de `/<Producto>/Apropiación`) es el candidato principal; (b) con `search_wiki` por nombre del producto y de sus workspaces, busca páginas TRS-9/Apropiación existentes (p. ej. de una corrida anterior o de un producto que comparta workspace; en este tenant también hay rutas del tipo `/Producto de Datos/<EquipoPD>/Apropiación/`). Para cada candidato anota: ruta exacta (con espacios), id, si está **vacía** o **con contenido** (y de qué fecha/alcance es). **Ojo:** `get_page` puede devolver `content` vacío aunque la página tenga contenido; para leerlo usa `get_page_content` (o confirma con `search_wiki`) antes de concluir que está vacía. Si el contenido previo tiene una **estructura distinta** a la plantilla que vas a publicar (p. ej. una página con 8 secciones donde la plantilla padre tiene 2), no decidas: presenta las opciones (reemplazar, conservar secciones extra, o mover el contenido previo a otra página) y recomienda una. Reglas: **no decidas entre candidatos plausibles**: preséntalos todos en el plan, recomienda uno con su motivo y deja la elección al usuario. Una página vacía o con contenido de una corrida anterior se **actualiza** (compara y avisa del contenido previo), no se duplica; las páginas de release van como subpáginas de la padre. Entrega: ruta exacta de cada página, crear/actualizar, y el adjunto `.xlsx`. **Publica solo con confirmación explícita** del usuario sobre ese plan (regla 5); si la sesión es no interactiva, entrega el plan y no publiques.
5. Recuerda el paso final del proceso: **gestionar el VoBo del líder de Servicio** una vez cargada la información en la wiki.

## 9. Fase 6 — Publicar en la wiki (solo con permiso del usuario)

Se llega aquí con el **plan de publicación** (§8.4) ya presentado. **No publiques nada sin la confirmación explícita del usuario** (regla 5); en modo no interactivo, termina en el plan.

1. **Pide el permiso** mostrando, por cada página: ruta exacta, **crear o actualizar**, un resumen del contenido (secciones y cantidad de pendientes `<DATO REQUERIDO>`) y, si es una actualización, **qué había** (fecha/alcance del contenido previo) para que el usuario sepa qué se sobrescribe. Pregunta también si quiere publicar con pendientes o llenarlos antes. Una confirmación vale **solo para ese plan**; si cambias contenido o ruta, vuelve a pedirla.
2. **Publica en este orden:** primero la página **padre** (crear/actualizar), luego la **hija** del release como subpágina de la padre. Usa la acción de crear/actualizar página de la herramienta `wiki` del MCP `azure-devops` (revisa sus acciones con `mcp_describe`). Parámetros: `wikiIdentifier` = `DemocratizacionDeDatos.wiki`, `project` = `DemocratizacionDeDatos`, `path` (con espacios, p. ej. `/Producto de Datos/<EquipoPD>/Apropiación/<Página>`), `content` = el `.md` generado tal cual.
3. **Adjunto del inventario:** si el MCP no permite subir adjuntos, no lo intentes por otras vías: dile al usuario la ruta local de `Inventario_Fabric_<Producto>.xlsx` y que lo adjunte manualmente a la página hija (la sección 7 enlaza la plantilla base de `.attachments`; ajusta el enlace al nombre del archivo cuando el usuario confirme que lo subió).
4. **Verifica** cada página con `get_page` (existe, contenido no vacío) y entrega al usuario los enlaces (`remoteUrl`).
5. **Registra** en `.coda/MEMORY.md` la ruta final publicada (no se versiona) y recuerda el **VoBo del líder de Servicio**.
