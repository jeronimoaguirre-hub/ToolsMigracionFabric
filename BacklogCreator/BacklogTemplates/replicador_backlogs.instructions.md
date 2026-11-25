---
description: Habilidad para automatizar la replicación y creación de la plantilla de Backlog (HU 01 al HU 09) para nuevos Productos de Datos en Azure DevOps.
---

# Generador de Backlog para Productos de Datos (Replicador)

Esta "Skill" te permite generar de manera automatizada y estructurada el conjunto estándar de Historias de Usuario (Product Backlog Items) necesarias para la fase de transición o creación de un nuevo **Producto de Datos**.

## 🛠️ ¿Cuándo utilizar esta instrucción?
Cuando el usuario solicite:
- "Crear el backlog para un nuevo producto de datos"
- "Replicar la plantilla de HUs de productos de datos"
- "Generar las historias estándar para el producto [X]"

## 📋 Requisitos Previos (Solicita lo que falte al usuario)
Antes de crear los elementos, necesitas saber:
1. **Nombre del Producto de Datos** (Que reemplazará `{{ProductName}}`).
2. **Dominio** (Que reemplazará `{{DomainName}}` - Ej: Perforación y Completamiento).
3. **Azure DevOps Project** (Ej. `DemocratizacionDeDatos`).
4. **Area Path** de destino.
5. **Iteration Path** de destino.
6. **Assignee / Correo asignado** (Opcional).
7. **Tags** adicionales (Opcional, Ej: `Proyectos`).

## 🚀 Pasos de Ejecución (Flujo para el Agente)

1. **Recuperar la plantilla base**:
   Lee el archivo JSON que contiene la estructura estándar: 
   `c:\Users\jeronimo.aguirre\Documents\ECP\Democratizacion-Etapa II\Transicion\BacklogTemplates\data_product_backlog.json`

2. **Reemplazo de Variables**:
   Por cada objeto en el JSON, procesa en memoria `System.Title`, `System.Description` y el array de tags.
   - Reemplaza la cadena literal `{{ProductName}}` por el nombre del producto indicado por el usuario.
   - Reemplaza la cadena literal `{{DomainName}}` por el nombre del dominio.
   - Si existen tags adicionales indicados por el usuario, concaténalos con los especificados en el objeto JSON.

3. **Invocación al Server de Azure DevOps**:
   Utiliza las herramientas `mcp_ado_wit_create_work_item` para iterar (o hacer un batch) sobre las 9 historias.
   Debes fijar obligatoriamente para CADA Work Item:
   - `System.WorkItemType`: "Product Backlog Item"
   - `System.Title`: *[Título con variable reemplazada]* (Format: Html / Markdown)
   - `System.Description`: *[Descripción con variable reemplazada]* (Format: Html)
   - `Microsoft.VSTS.Common.AcceptanceCriteria`: *[Criterios de Aceptación del JSON]* (Format: Html) 
   - `System.AreaPath`: *[Area Path definida]*
   - `System.IterationPath`: *[Iteration Path definida]*
   - `System.AssignedTo`: *[Correo Asignado]* (Si existe)
   - `System.Tags`: *[Lista final de Tags separada por comas, incluyendo la variable de {{ProductName}} reemplazada y 'Entregable' según el JSON]*
   
4. **Confirmación**:
   Entrégale al usuario un recuento con los IDs de las tareas creadas exitosamente y su respectivo Link/Título para verificación.
