# **<DATO REQUERIDO: NOMBRE DEL WORKSPACE>**

## **1. Ambientes**

| Ambiente | Capa | Nombre Del WorkSpace | URL | Lider Funcional | Responsable del Dominio | Roles asignados | IDWorkspace |
|----------|------|----------------------|-----|-----------------|-------------------------|-----------------|-------------|
| DEVQA | <DATO REQUERIDO: CAPA BRONZE/SILVER/GOLD> | <DATO REQUERIDO: NOMBRE DEL WORKSPACE> | <DATO REQUERIDO: LINK DEL WORKSPACE> | <DATO REQUERIDO: LIDER FUNCIONAL> | <DATO REQUERIDO: RESPONSABLE DEL DOMINIO> | <DATO REQUERIDO: ROLES ASIGNADOS> | <DATO REQUERIDO: IDWORKSPACE> |
| PRD | <DATO REQUERIDO: CAPA BRONZE/SILVER/GOLD> | <DATO REQUERIDO: NOMBRE DEL WORKSPACE> | <DATO REQUERIDO: LINK DEL WORKSPACE> | <DATO REQUERIDO: LIDER FUNCIONAL> | <DATO REQUERIDO: RESPONSABLE DEL DOMINIO> | <DATO REQUERIDO: ROLES ASIGNADOS> | <DATO REQUERIDO: IDWORKSPACE> |

## **2. Fuentes de Datos y Conexiones**

Documente las fuentes de datos utilizadas en el proyecto o proceso. Es fundamental especificar la tecnología (`Tipo de Conexión`), la ubicación (`Instancia`, `Nombre BD`), y la credencial de acceso (`Usuario //`). **Objetivo:** Establecer un inventario claro de las fuentes de información, facilitando el mantenimiento y la auditoría.

| Nombre de la Fuente | Ambiente | Metodo de autenticacion | Nombre de Conexión | Tipo de Conexión | HostName/Ip | Instancia/Nombre BD | Nombre Gateway | Fecha Vencimiento credenciales | Responsable | Observación | Imagen |
|---------------------|----------|-------------------------|--------------------|------------------|-------------|---------------------|----------------|--------------------------------|-------------|-------------|--------|
| <DATO REQUERIDO: NOMBRE DE LA FUENTE> | <DATO REQUERIDO: AMBIENTE> | <DATO REQUERIDO: METODO DE AUTENTICACION> | <DATO REQUERIDO: NOMBRE DE CONEXION> | <DATO REQUERIDO: TIPO DE CONEXION> | <DATO REQUERIDO: HOSTNAME/IP> | <DATO REQUERIDO: INSTANCIA/NOMBRE BD> | <DATO REQUERIDO: NOMBRE GATEWAY> | <DATO REQUERIDO: FECHA VENCIMIENTO CREDENCIALES> | <DATO REQUERIDO: RESPONSABLE> | <DATO REQUERIDO: OBSERVACION> | <DATO REQUERIDO: IMAGEN> |

## **3. Tipo de Archivos**

Identifique y clasifique los tipos de archivos generados o consumidos por el proceso. Especifique el sistema de almacenamiento (`Repositorio`), la ruta exacta (`Ubicación`) y la forma de acceso (`Conexión o Usuario`). **Objetivo:** Controlar y estandarizar la gestión de archivos, asegurando su correcta localización y seguridad.

| Tipo de Archivo | Nombre Archivo | Repositorio | Ubicación | Responsable | Conexión o Usuario | Particionamiento | Nombre Conexión |
|-----------------|----------------|-------------|-----------|-------------|--------------------|------------------|-----------------|
| <DATO REQUERIDO: TIPO DE ARCHIVO> | <DATO REQUERIDO: NOMBRE ARCHIVO> | <DATO REQUERIDO: REPOSITORIO> | <DATO REQUERIDO: UBICACION> | <DATO REQUERIDO: RESPONSABLE> | <DATO REQUERIDO: CONEXION O USUARIO> | <DATO REQUERIDO: PARTICIONAMIENTO> | <DATO REQUERIDO: NOMBRE CONEXION> |

## **4. Modelo de Datos**

Indique el **link de la hoja del modelo de datos** (URL) y complete la tabla especificando la versión para controlar su modificación. **Objetivo:** Mantener un historial de versiones y asegurar que el equipo trabaje con el modelo validado más reciente.

Link del modelo de datos: <DATO REQUERIDO: URL DEL MODELO DE DATOS>

| Versión | Nombre | Editable | Dependencias | Fecha | Observación |
|---------|--------|----------|--------------|-------|-------------|
| <DATO REQUERIDO: VERSION> | <DATO REQUERIDO: NOMBRE> | <DATO REQUERIDO: EDITABLE> | <DATO REQUERIDO: DEPENDENCIAS> | <DATO REQUERIDO: FECHA> | <DATO REQUERIDO: OBSERVACION> |

## **5. Arquitectura**

Indique el **link de la hoja de arquitectura** (URL) y complete la tabla especificando la versión para controlar su modificación. **Objetivo:** Mantener un historial de versiones y asegurar que el equipo trabaje con la arquitectura validada más reciente.

| Workspace | Diagrama de arquitectura | Modelo entidad relacion |
|-----------|--------------------------|-------------------------|
| <DATO REQUERIDO: WORKSPACE> | <DATO REQUERIDO: DIAGRAMA DE ARQUITECTURA> | <DATO REQUERIDO: MODELO ENTIDAD RELACION> |

Registre cada versión del producto o sistema que ha sido formalmente entregada al área de Operaciones para su puesta en producción o gestión continua. Especifique la `Versión`, el `Nombre` de la entrega, y si el código/documento entregado es `Editable` por el equipo de Operaciones. **Objetivo:** Trazar las versiones productivas y las responsabilidades posteriores a la entrega.

| Versión | Nombre | Editable | Fecha | Observación |
|---------|--------|----------|-------|-------------|
| <DATO REQUERIDO: VERSION> | <DATO REQUERIDO: NOMBRE> | <DATO REQUERIDO: EDITABLE> | <DATO REQUERIDO: FECHA> | <DATO REQUERIDO: OBSERVACION> |

## **6. Pipeline Historicos e Incrementales**

Esta sección es importante porque permite identificar y controlar los pipelines que procesan la información, dejando claro **qué versión existe**, **cómo se llama**, **si es editable**, **cada cuánto se ejecuta** y **cuánto tarda en promedio**.

Su objetivo es asegurar trazabilidad, control de cambios y visibilidad operativa sobre los procesos de carga de datos, facilitando el mantenimiento y la operación del entorno.

| Versión | Nombre | Editable | Fecha | Observación | Frecuencia extraccion y ejecución | Duracion Promedio carga/Volumen Prom datos |
|---------|--------|----------|-------|-------------|-----------------------------------|--------------------------------------------|
| <DATO REQUERIDO: VERSION> | <DATO REQUERIDO: NOMBRE> | <DATO REQUERIDO: EDITABLE> | <DATO REQUERIDO: FECHA> | <DATO REQUERIDO: OBSERVACION> | <DATO REQUERIDO: FRECUENCIA EXTRACCION Y EJECUCION> | <DATO REQUERIDO: DURACION PROMEDIO CARGA/VOLUMEN PROM DATOS> |

## **7. Inventario Objetos**

Documente con precisión la jerarquía y el propósito de las carpetas dentro de la estructura de su Lakehouse en Fabric. Especifique el **Nombre de la Carpeta** principal y sus **Subcarpetas**. Detalle el **Tipo de Objeto** (ej. tabla Delta, archivo Parquet, Notebook) que reside en la ruta y complete la **Descripción** para aclarar su uso y contenido. **Objetivo:** Estandarizar la arquitectura de datos, facilitar la navegación de los usuarios y garantizar el cumplimiento de las políticas de almacenamiento.

Debe incluir el detalle de **Pipelines historicos e incrementales**, Descripción, Conexiones y Programaciones.

Editable Plantilla Base: [Plantilla - Inventario_Fabric_WS_XXX.xlsx](/.attachments/Plantilla%20-%20Inventario_Fabric_WS_XXX-7d6c527e-7ab7-4cf4-8132-de7c09af9fd6.xlsx)

| Ambiente | Capa | Nombre de Carpeta | Subcarpeta | Nombre | Tipo de Objeto | Descripción | Frecuencia de actualización | Duración promedio |
|----------|------|-------------------|------------|--------|----------------|-------------|-----------------------------|-------------------|
| <DATO REQUERIDO: AMBIENTE> | <DATO REQUERIDO: CAPA> | <DATO REQUERIDO: NOMBRE DE CARPETA> | <DATO REQUERIDO: SUBCARPETA> | <DATO REQUERIDO: NOMBRE> | <DATO REQUERIDO: TIPO DE OBJETO> | <DATO REQUERIDO: DESCRIPCION> | <DATO REQUERIDO: FRECUENCIA DE ACTUALIZACION> | <DATO REQUERIDO: DURACION PROMEDIO> |

## **8. Capacitación funcional y tecnica**

| Fecha | Versión | Documentos | Evidencia | Descripción |
|-------|---------|------------|-----------|-------------|
| <DATO REQUERIDO: FECHA DD-MM-AAAA> | <DATO REQUERIDO: VERSION> | <DATO REQUERIDO: DOCUMENTOS> | <DATO REQUERIDO: EVIDENCIA> | <DATO REQUERIDO: DESCRIPCION> |
| <DATO REQUERIDO: DD-MM-AAAA> | <DATO REQUERIDO: VERSION> | <DATO REQUERIDO: DOCUMENTOS> | <DATO REQUERIDO: EVIDENCIA> | <DATO REQUERIDO: DESCRIPCION> |
