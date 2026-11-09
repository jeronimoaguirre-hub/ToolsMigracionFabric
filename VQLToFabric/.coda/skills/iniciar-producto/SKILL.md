---
name: iniciar-producto
description: Onboarding de un producto nuevo — configura producto.yml y CONTEXTO_PRODUCTO.md, verifica archivos VQL locales y el entorno opcional de Fabric. Se corre una vez por producto, después de clonar la plantilla.
---

# /iniciar-producto

Se corre **una vez por producto**, después de clonar la plantilla. La sesión
principal de Coda conversa con el desarrollador y prepara la configuración del
harness. Esta skill no accede a Denodo.

## Pasos

1. **Estado actual.** Lee `producto.yml` y `CONTEXTO_PRODUCTO.md`. Si ya están
   configurados, pregunta si quiere revisarlos o actualizarlos en vez de empezar
   de cero.

2. **Entrevista corta** con `ask_user` (máx. 4 preguntas por ronda), solo lo
   que no puedas deducir de los archivos:
   - Nombre y descripción breve del producto.
   - Workspace, warehouse y lakehouse(s) Gold en Fabric; esquemas destino
     (report/projection) y esquemas fuente del lakehouse.
   - Directorio de VQL, prefijos y convenciones de vistas, y patrones para
     identificar los orígenes físicos. Infiera esto de los VQL locales cuando
     sea posible; si no, pregúntalo.
   - Cómo revisa y despliega el ingeniero el DDL (método documental).

3. **Escribe** `producto.yml` y las secciones aplicables de
   `CONTEXTO_PRODUCTO.md`. No inventes: lo desconocido queda como `TODO`.
   Configura el origen lógico bajo `vql:`; no pidas nombre de usuario,
   contraseña, servidor ni base Denodo.

4. **Verifica el entorno** sin imprimir secretos:
   - Comprueba solo si existe `.env`; si falta, indica copiar `.env.example`.
     Nunca lo abras ni muestres su contenido.
   - Comprueba si existe `.venv`; si no, indica correr `uv sync`.
   - Si las consultas a Fabric están en alcance, comprueba el driver ODBC de SQL
     Server de la skill `fabric-odbc-query`.
   - Comprueba `az account show` solo para el uso de Fabric/MCP, sin exponer
     información sensible innecesaria.
   - Comprueba si `vql.directorio` contiene archivos `.vql`; si no, pide que el
     equipo exporte y coloque los archivos localmente. No intentes conectarte a
     Denodo para obtenerlos.

5. **Prueba opcional de Fabric** (pide confirmación antes): una consulta
   trivial `SELECT 1` mediante `fabric-odbc-query`. Nunca pruebes una conexión
   a Denodo.

6. **Resumen**: qué quedó listo y qué falta, con el paso exacto. Recuerda que
   los agentes de `.coda/agents/` se cargan al iniciar la sesión (reinicia Coda
   si se crearon o editaron). El siguiente paso es
   `/migrar-vista {nombre_vista}`.

## Reglas

- Nunca leas ni muestres `.env`, credenciales, tokens ni cachés.
- Nunca solicites credenciales ni configuración de conexión a Denodo.
- Nunca te conectes a Denodo ni busques VQL fuera de los archivos locales.
- Si `producto.yml` ya tenía datos, no los sobrescribas sin confirmación.
- Todo cambio a `producto.yml` / `CONTEXTO_PRODUCTO.md` es una edición asistida
  por el desarrollador: muéstrale el resultado final.
