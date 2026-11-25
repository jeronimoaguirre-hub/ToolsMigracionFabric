# ToolsMigracionFabric
Repositorio de herramientas Agenticas y no agenticas que optimizan el desarrollo de la migración a Microsoft Fabric

> **Nota:** las herramientas agenticas de este repositorio están diseñadas para utilizarse con **CODA**.

## Cómo usar este repositorio

Este repo es un **catálogo de plantillas**: no vive aquí el desarrollo de los productos; cuando necesitan una herramienta, simplemente **clonan la carpeta correspondiente** y la usan en su propio entorno/repositorio.

- No se espera sincronización continua con este repo (`fetch`/`merge` de remotos).
- Cada herramienta es autocontenida: revisa su README para las instrucciones de uso.

## Contenido

| Herramienta | Tipo | Descripción |
|---|---|---|
| [`VQLToFabric/`](VQLToFabric/README.md) | Agéntica | Harness para traducir vistas VQL (Denodo) a T-SQL para la capa Gold de Microsoft Fabric. Los agentes exploran dependencias, proponen DDL y consultan Fabric en modo lectura; el ingeniero revisa y despliega. |
| [`TransicionAgent/`](TransicionAgent/README.md) | Agéntica | Genera la documentación de transición TRS - 9 de un producto de datos en Fabric (Inventario Fabric `.xlsx` + páginas padre/hija) con datos reales de solo lectura, y la publica en la wiki de Azure DevOps solo con permiso del usuario. |
| [`BacklogCreator/`](BacklogCreator/README.md) | Agéntica | Crea los 9 Product Backlog Items estándar (HU 01–HU 09) de un nuevo Producto de Datos en Azure DevOps vía MCP, con preview obligatorio antes de crear. |

> **Mantener actualizado:** al agregar una herramienta nueva al repositorio, añade una fila a esta tabla con su nombre, tipo (agéntica / no agéntica) y una descripción de una línea.
