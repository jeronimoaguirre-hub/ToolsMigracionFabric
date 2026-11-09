# Plantilla de traducción VQL → T-SQL (Fabric Gold)

Harness para que los equipos de datos investiguen archivos VQL exportados localmente, traduzcan vistas a T-SQL para Microsoft Fabric y consulten el Warehouse de Fabric en modo lectura. Los agentes exploran dependencias y proponen DDL; **el ingeniero revisa y despliega**. El harness no se conecta a Denodo ni certifica equivalencia de datos mediante comparaciones en origen.

## Qué incluye

```
AGENTS.md                 Reglas del harness
producto.yml              Configuración del producto: warehouse, esquemas, prefijos
CONTEXTO_PRODUCTO.md      Contexto del producto para los agentes
denodo-vql/               Archivos VQL exportados (solo lectura local)
ledger/                   VQL analizada, decisiones y estado por vista
ddl/                      DDL T-SQL propuesto (lo despliega el ingeniero)
knowledge/
  patrones-base.md        Patrones comunes de traducción
  funciones-vql-tsql.md   Tabla de equivalencias de funciones
  patrones-producto.md    Patrones específicos del producto
.coda/
  agents/                 Agentes de exploración, diseño T-SQL y revisión estática
  skills/                 /iniciar-producto, /migrar-vista y fabric-odbc-query
  config.json             Permisos del harness
  mcp.json                Configuración opcional del MCP de Fabric
```

## Puesta en marcha por producto

### Requisitos

- Git y acceso al repositorio de la plantilla.
- Python 3.12 o superior y `uv`, instalados por el método aprobado por tu organización.
- Coda instalado y acceso habilitado a sus agentes y skills.
- Para consultar Fabric mediante ODBC: Microsoft ODBC Driver 17 o 18 for SQL Server.
- Para usar el MCP opcional de Fabric: Azure CLI, el SDK de .NET que proporciona `dnx` y acceso de Azure a Fabric.

### Crear el repositorio del producto

Cada producto tiene su propio repositorio para configuración, VQL local, ledgers y DDL. Para conservar el historial compartido con la plantilla:

1. Crea un repositorio vacío para el producto en el servidor Git de tu organización, de acuerdo con el proceso del equipo.
2. Clona la plantilla y configura ambos remotos. Reemplaza los valores entre `<...>` por los aprobados por tu equipo:

   ```bash
   git clone <url-de-la-plantilla> NombreProducto
   cd NombreProducto
   git remote rename origin template
   git remote add origin <url-del-repositorio-del-producto>
   git push -u origin <rama-inicial>
   ```

3. Mantén `template` apuntando a la plantilla y `origin` al repositorio del producto. Consulta `CONTRIBUTING.md` para recibir actualizaciones revisadas.

Los ingenieros ejecutan las operaciones Git manualmente; Coda tiene prohibido hacer `push` y modificar remotos.

### Configurar y empezar

1. En la raíz del repositorio, instala dependencias:

   ```bash
   uv sync
   ```

2. Copia `.env.example` a `.env` y completa los valores de Fabric. **Nunca compartas ni versionas `.env`**.
3. Si usarás el MCP de Fabric, ejecuta `az login` con la cuenta autorizada y verifica que `dnx` esté disponible.
4. Coloca en `denodo-vql/` los archivos VQL exportados que te proporcionó el equipo de origen. El harness solo los analiza localmente; no necesita acceso ni credenciales de Denodo.
5. Abre el repositorio en Coda y corre `/iniciar-producto` para configurar `producto.yml` y `CONTEXTO_PRODUCTO.md`.
6. Reinicia la sesión de Coda si acabas de instalar o actualizar agentes o skills.

## Flujo por vista

```text
/migrar-vista rv_mi_vista  → explora los VQL locales y propone DDL T-SQL
Revisión humana            → revisas ddl/rv_mi_vista.sql y decides si desplegarlo en Fabric
```

La skill `fabric-odbc-query` permite consultar Fabric en solo lectura, por ejemplo para revisar objetos y metadatos existentes. El ledger registra la evidencia estática y las consultas efectivamente ejecutadas en Fabric; no declara equivalencia de filas contra Denodo.

## Qué es de quién

| Dueño | Archivos |
|---|---|
| Plantilla | `.coda/**`, `AGENTS.md`, `knowledge/patrones-base.md`, `knowledge/funciones-vql-tsql.md`, `pyproject.toml`, `uv.lock` |
| Equipo del producto | `producto.yml`, `CONTEXTO_PRODUCTO.md`, `denodo-vql/`, `ledger/`, `ddl/`, `knowledge/patrones-producto.md`, `.env` local |

Para proponer cambios generales o recibir actualizaciones, consulta `CONTRIBUTING.md`. Revisa los cambios y resuelve conflictos antes de fusionar.

## Seguridad y límites

- El harness solo consulta Fabric en modo lectura. Nunca ejecuta DDL/DML ni despliega cambios.
- No incluye conexión a Denodo. No pongas credenciales de Denodo en `.env`; los VQL locales pueden tener metadatos internos y deben almacenarse en una ubicación autorizada por tu organización.
- No compartas `.env`, tokens, cachés de autenticación ni datos sensibles.
- La traducción no equivale a una prueba de resultados. El ingeniero y el dueño de negocio deben resolver las diferencias o validar los resultados mediante el proceso autorizado de su organización.
