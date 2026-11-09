# Traducción VQL → T-SQL (Fabric Warehouse, capa Gold)

Este repo es una **plantilla**: cada producto de datos tiene su propia copia.
El objetivo es investigar archivos VQL exportados localmente, traducir sus vistas
a T-SQL para la capa Gold de Microsoft Fabric y consultar Fabric en modo lectura
cuando sea necesario. Un ingeniero revisa y despliega el DDL propuesto. El
harness no se conecta a Denodo ni ejecuta pruebas de equivalencia en origen.

@CONTEXTO_PRODUCTO.md

La configuración estructurada del producto (nombres de warehouse, esquemas,
prefijos de vistas y directorio de VQL local) vive en `producto.yml`. **Léelo
antes de empezar cualquier tarea** — nada de nombres de producto va hardcodeado
en agentes ni scripts.

Si `producto.yml` todavía tiene valores `TODO`, el desarrollador no ha
corrido `/iniciar-producto`: pídele que lo haga antes de migrar nada.

## Mapa del repo

| Carpeta / archivo | Quién lo edita | Qué es |
|---|---|---|
| `.coda/` (agentes, skills, config, mcp) | **Plantilla** (se actualiza vía git) | El harness |
| `knowledge/patrones-base.md`, `knowledge/funciones-vql-tsql.md` | **Plantilla** | Conocimiento común de traducción |
| `producto.yml`, `CONTEXTO_PRODUCTO.md` | **Desarrollador** | Configuración y contexto del producto |
| `denodo-vql/` | **Desarrollador** | VQL exportado localmente; nunca se consulta Denodo desde el harness |
| `knowledge/patrones-producto.md` | **Desarrollador / agentes (con confirmación)** | Patrones propios de este producto |
| `ledger/{vista}.md` | **Agentes** | Exploración, decisiones y estado del DDL — única fuente de verdad entre agentes |
| `ddl/{vista}.sql` | **Agente `tsql-view-architect`** | DDL propuesto; el ingeniero lo revisa y despliega en Fabric |

Regla de oro para no romper las actualizaciones de la plantilla: **no edites
archivos de `.coda/` ni los `*-base.md` en tu copia**. Si algo del harness
no te sirve, propón el cambio en el repo de la plantilla. Lo específico de tu
producto va en `producto.yml`, `CONTEXTO_PRODUCTO.md` y `knowledge/patrones-producto.md`.

## Flujo estándar por vista

`/migrar-vista {nombre_vista}` orquesta la exploración local y la propuesta de
DDL:

1. **Explorar** — `vql-explorer` localiza la VQL en `denodo-vql/` y traza su
   cadena de dependencias a partir de los archivos exportados
   (`ledger/{vista}.md`, estado `explorado`). No se conecta a Denodo.
2. **Diseñar** — `tsql-view-architect` traduce a T-SQL, detecta patrones de
   riesgo y puede consultar metadatos/definiciones existentes en Fabric en solo
   lectura. Escribe `ddl/{vista}.sql` y el diagnóstico (estado `ddl_propuesto`).
3. **🛑 Compuerta humana** — el ingeniero revisa el DDL y, si lo aprueba, lo
   despliega en Fabric. Ningún agente despliega ni certifica equivalencia de
   datos contra Denodo.

La revisión asistida se limita a analizar estáticamente la VQL local y el DDL,
y a consultar metadatos de Fabric en modo lectura cuando sea necesario. No se
afirma equivalencia en ejecución.

## Qué puede hacer la IA, qué no, y qué debe preguntar

**Puede, sin preguntar**
- Leer VQL, DDL, ledgers y conocimiento del repo.
- Escribir/editar en `ledger/`, `ddl/` y `knowledge/patrones-producto.md` (solo proponer en este último, ver abajo).
- Ejecutar consultas **de solo lectura** (`SELECT`, `INFORMATION_SCHEMA`) contra Fabric con la skill `fabric-odbc-query`.
- Leer y analizar archivos VQL locales en `denodo-vql/`; no se permite conexión a Denodo.

**Debe preguntar primero**
- Agregar un patrón nuevo a `knowledge/patrones-producto.md` (se propone en el ledger y se agrega con confirmación del usuario).
- Ejecutar consultas pesadas en Fabric (sin filtro sobre tablas grandes); pide confirmación antes.
- Cualquier acción que no esté cubierta por las reglas de permisos de `.coda/config.json`.

**Nunca**
- Ejecutar DDL/DML en el Warehouse o el Lakehouse (`CREATE`, `ALTER`, `DROP`, `INSERT`, `UPDATE`, `DELETE`, `MERGE`). Se propone el DDL, lo despliega el ingeniero.
- Leer o imprimir `.env`, caches de tokens (`*.bin`) ni credenciales.
- Hacer `git push`, abrir PRs o ejecutar pipelines.
- Afirmar equivalencia de datos en ejecución entre Denodo y Fabric: el harness no consulta Denodo. Las diferencias potenciales se documentan como observaciones estáticas para revisión del ingeniero y del dueño de negocio.
- Inventar un valor de parámetro, una columna o una dependencia que no esté en la VQL/DDL/ledger.

## Reglas para todos los agentes

- Lee `knowledge/patrones-base.md`, `knowledge/patrones-producto.md` y `knowledge/funciones-vql-tsql.md` antes de traducir. No hay que redescubrir lo ya conocido.
- Nunca asumas que una columna con nombre parecido a un parámetro es el mecanismo de filtro real — confírmalo contra la VQL fuente (Patrón P01).
- T-SQL no tiene parámetros de vista. Todo `USING PARAMETERS` se resuelve según `knowledge/patrones-base.md` (P01, P02, P08, P14), nunca con `CAST(NULL AS ...)`.
- Analiza **comportamiento**, no solo sintaxis: verifica estáticamente filtros, parámetros, joins y transformaciones contra la VQL fuente. No declares equivalencia de filas, ya que no se consulta Denodo.
- Toda consulta de solo lectura que ejecutes en Fabric queda en el ledger con **la query exacta y el resultado**, no solo la conclusión.
- Distingue los hallazgos estáticos de las consultas ejecutadas en Fabric. No reportes como ejecutada una consulta pendiente; deja su query exacta para revisión manual.
- Un hallazgo que no esté en los patrones se **propone** en el ledger (sección "¿Patrón nuevo?"); solo se agrega al catálogo con confirmación del usuario.
- El ledger es la única memoria compartida: los subagentes no se ven entre sí.

## Agentes

| Agente | Cuándo | Modelo sugerido (tier Coda) |
|---|---|---|
| `vql-explorer` | Localizar VQL local y trazar dependencias hasta el origen descrito en los archivos | fast |
| `tsql-view-architect` | Construir o corregir el DDL T-SQL de una vista Gold | deep (o smart) |
| `view-auditor` | Revisión estática de la traducción VQL local ↔ T-SQL; no certifica equivalencia de datos | deep |

Los agentes de `.coda/agents/` se cargan al iniciar la sesión de Coda:
**reinicia la sesión** si se acaban de crear o editar.

## Conexiones y datos

- Fabric: skill `fabric-odbc-query` para consultas de solo lectura (login interactivo de Entra ID con caché de sesión).
- VQL de origen: archivos exportados y entregados por el ingeniero en `denodo-vql/`. El harness solo los lee localmente; no solicita credenciales ni se conecta a Denodo.
- `.env` solo requiere los valores de Fabric definidos en `.env.example`; nunca se versiona.
- MCP de Fabric (opcional) en `.coda/mcp.json`; fija `AZURE_TOKEN_CREDENTIALS=AzureCliCredential` para evitar que se autentique con otra cuenta/tenant. Requiere `az login` con la cuenta correcta y reiniciar Coda tras cambiar credenciales.
