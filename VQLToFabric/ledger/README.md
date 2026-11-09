# ledger/

Un archivo por vista traducida: `ledger/{nombre_vista}.md`, creado desde
`_PLANTILLA.md`. Registra los archivos VQL locales analizados, las decisiones
de traducción, el DDL propuesto y la revisión estática. Es la fuente compartida
entre invocaciones de agentes.

Estados de trabajo sugeridos: `explorado` → `ddl_propuesto` →
`desplegado_por_ingeniero` → `revision_estatica_completada`; usa
`pendiente_decision` cuando haya una decisión funcional que deba tomar una
persona responsable.

El estado no representa una equivalencia de datos: el harness no se conecta a
Denodo ni compara resultados en ejecución. Las consultas que se ejecuten contra
Fabric deben ser de solo lectura y registrarse con query exacta y resultado.
