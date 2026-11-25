---
name: replicar-backlog
description: Crea los 9 Product Backlog Items estándar (HU 01–HU 09) para un nuevo Producto de Datos en Azure DevOps, usando el MCP de Azure DevOps. Reemplaza variables {{ProductName}} y {{DomainName}} sobre la plantilla JSON y crea los work items con formato HTML. Siempre pide confirmación explícita antes de crear nada.
---

# /replicar-backlog

Genera el conjunto estándar de Historias de Usuario (Product Backlog Items)
necesarias para la fase de transición o creación de un nuevo **Producto de Datos**
en Azure DevOps, usando el MCP de Azure DevOps de Coda.

## Cuándo usarla

Cuando el usuario solicite:
- "Crear el backlog para un nuevo producto de datos"
- "Replicar la plantilla de HUs de productos de datos"
- "Generar las historias estándar para el producto [X]"

## Requisitos previos

Antes de crear nada, necesitas saber (pide con `ask_user` solo lo que falte):

1. **Nombre del Producto de Datos** → reemplaza `{{ProductName}}`.
2. **Dominio** → reemplaza `{{DomainName}}` (ej. "Perforación y Completamiento").
3. **Azure DevOps Project** (ej. `DemocratizacionDeDatos`).
4. **Area Path** de destino.
5. **Iteration Path** de destino.
6. **Assignee / correo asignado** (opcional).
7. **Tags adicionales** (opcional, ej. `Proyectos`).

## Pasos

1. **Leer la plantilla base.** Lee el archivo JSON con la estructura estándar:
   `BacklogCreator/BacklogTemplates/data_product_backlog.json`
   Contiene 9 objetos con `title`, `description` (HTML), `tags` y
   `acceptanceCriteria` (HTML).

2. **Reemplazo de variables.** Por cada objeto, procesa en memoria `title`,
   `description`, `acceptanceCriteria` y `tags`:
   - Reemplaza la cadena literal `{{ProductName}}` por el nombre del producto.
   - Reemplaza la cadena literal `{{DomainName}}` por el nombre del dominio.
   - Si hay tags adicionales, concaténalos con los del objeto JSON.

3. **Validación previa (recomendada).** Antes de crear nada:
   - Verifica que el proyecto existe con `core_list_projects` (MCP azure-devops).
   - Verifica que el tipo "Product Backlog Item" existe con
     `wit_work_item` action=`get_type`, `workItemType="Product Backlog Item"`.
   - Si el area path o iteration path no se pueden confirmar, avísalo al usuario
     y pide confirmación para continuar de todos modos.

4. **🛑 Compuerta humana.** Muestra un **preview** (dry-run) con la lista de los
   9 títulos ya con variables reemplazadas, el area/iteration path, assignee y
   tags finales. **No crees nada sin confirmación explícita del usuario.**

5. **Creación de work items.** Con el MCP azure-devops, herramienta
   `wit_work_item_write`:
   - `action`: `create`
   - `project`: el proyecto indicado
   - `workItemType`: `Product Backlog Item`
   - `fields` (format `Html` para los campos de texto largo):
     - `System.Title` — título con variables reemplazadas
     - `System.Description` — descripción con variables reemplazadas (Html)
     - `Microsoft.VSTS.Common.AcceptanceCriteria` — criterios de aceptación (Html)
     - `System.AreaPath` — area path definida
     - `System.IterationPath` — iteration path definida
     - `System.AssignedTo` — correo asignado (si existe)
     - `System.Tags` — lista final de tags separada por comas (incluye el
       nombre del producto y `Entregable` según el JSON)

   Crea los 9 items uno por uno. Si uno falla, continúa con los demás y reporta
   el error al final. No hagas batch silencioso: reporta cada resultado.

6. **Confirmación final.** Entrega un recuento con los IDs de los work items
   creados exitosamente, su título y el link para verificación
   (`https://dev.azure.com/{org}/{project}/_workitems/edit/{id}`).

## Reglas

- Nunca crees work items sin confirmación explícita del usuario (compuerta humana).
- Nunca inventes valores: si falta un dato, pregúntalo.
- Si un item falla, continúa con los demás y reporta el error al final.
- Reporta cada ID creado con su título y URL.
- No publiques en ningún backlog sin que el usuario lo pida explícitamente.
