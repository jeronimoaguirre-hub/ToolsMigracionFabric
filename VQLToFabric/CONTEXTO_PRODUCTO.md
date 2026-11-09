# Contexto del producto

> Dueño: el desarrollador. Este archivo lo importa `AGENTS.md`, así que todo lo
> que escribas aquí lo ven los agentes. Mantenlo corto y accionable. Se llena
> con `/iniciar-producto`.

## Qué es el producto

TODO — qué datos expone, quién lo consume (reportes, áreas), cuántas vistas aprox.

## Archivos VQL de origen

TODO — dónde se exportó el VQL, cómo están organizadas las vistas (capas
`bv_`/`rv_`) y qué orígenes físicos se describen en esos archivos. El harness
solo lee los VQL locales; no se conecta a Denodo.

## Arquitectura de destino (Fabric)

TODO — workspace Gold, warehouse y lakehouse(s) fuente, además de información
de ingesta que ayude a interpretar los datos disponibles en Fabric.

## Convenciones del producto

TODO — nombres de vistas en Fabric (¿mismo nombre que en el VQL?), esquemas,
columnas obligatorias y reglas de naming.

## Particularidades conocidas

TODO — cosas que un agente nuevo debe saber antes de tocar este producto
(ej. "las vistas con prefijo X siempre dependen de Calculation Views",
"el pipeline de carga corre a las 6am y 2pm").

## Quién decide qué

TODO — dueño de negocio para decisiones de cambio de comportamiento, y
quién despliega DDL.
