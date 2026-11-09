# ToolsMigracionFabric
Repositorio de herramientas Agenticas y no agenticas que optimizan el desarrollo de la migración a Microsoft Fabric

> **Nota:** las herramientas agenticas de este repositorio están diseñadas para utilizarse con **CODA**.

## Cómo usar este repositorio

Este repo es un **catálogo de plantillas**: no vive aquí el desarrollo de los productos. Los ingenieros de datos trabajan principalmente en Microsoft Fabric y en repositorios de Azure DevOps; cuando necesitan una herramienta, simplemente **clonan la carpeta correspondiente** y la usan en su propio entorno/repositorio.

- No se espera sincronización continua con este repo (`fetch`/`merge` de remotos).
- Cada herramienta es autocontenida: revisa su README para las instrucciones de uso.

## Contenido

| Herramienta | Tipo | Descripción |
|---|---|---|
| [`VQLToFabric/`](VQLToFabric/README.md) | Agéntica | Harness para traducir vistas VQL (Denodo) a T-SQL para la capa Gold de Microsoft Fabric. Los agentes exploran dependencias, proponen DDL y consultan Fabric en modo lectura; el ingeniero revisa y despliega. |

> **Mantener actualizado:** al agregar una herramienta nueva al repositorio, añade una fila a esta tabla con su nombre, tipo (agéntica / no agéntica) y una descripción de una línea.
