# Contribuir a la plantilla

Esta guía aplica a las mejoras generales del harness. Los datos específicos de un producto (VQL, warehouse, esquemas, ledgers y DDL) pertenecen al repositorio de ese producto y no deben agregarse a la plantilla.

## Proponer una mejora

1. Confirma con el responsable del repositorio cuál es el flujo aprobado para ramas y revisiones.
2. Describe el problema y su impacto en un caso genérico, sin copiar VQL, credenciales, resultados ni metadatos internos de un producto.
3. Mantén los cambios acotados a la plantilla: harness en `.coda/`, reglas en `AGENTS.md` y patrones comunes en `knowledge/*-base.md`.
4. Comprueba las referencias, ejemplos y reglas de permisos afectadas. Ejecuta las validaciones locales disponibles y registra cualquier comprobación que requiera acceso a Fabric.
5. Envía el cambio por el mecanismo de revisión aprobado por la organización. No publiques ni fusiones cambios sin autorización.

## Recibir actualizaciones en un repositorio de producto

Cada repositorio de producto conserva su propio `origin`; el remoto de la plantilla se configura aparte como `template`. Los ingenieros deben ejecutar las operaciones Git manualmente y seguir el proceso de aprobación del equipo. Un flujo habitual es:

```bash
git fetch template
git log --oneline HEAD..template/<rama-principal>
git merge template/<rama-principal>
```

Reemplaza `<rama-principal>` por la rama principal acordada para la plantilla. Revisa el diff antes de fusionar, resuelve conflictos y ejecuta las validaciones del proyecto. No supongas que la fusión será automática: adapta cambios que coincidan con archivos del producto y conserva su configuración.

## Seguridad

- No agregues `.env`, tokens, cachés, credenciales ni VQL o datos de negocio de un producto.
- Revisa las reglas de `.gitignore` y `.coda/config.json` antes de proponer cambios que afecten archivos sensibles, permisos o comandos ejecutables.
- Las validaciones o consultas contra Fabric deben ser de solo lectura; no ejecutes ni propongas escrituras como parte de una comprobación.
