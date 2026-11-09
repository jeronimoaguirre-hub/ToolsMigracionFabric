---
name: migrar-vista
description: Orquesta la traducción de una vista desde archivos VQL locales a T-SQL en la capa Gold de Fabric — explora dependencias, diseña el DDL y se detiene para que el ingeniero lo revise y despliegue. Úsala mencionando el nombre de la vista (ej. "migrar-vista rv_xxx_yyy_v").
---

# /migrar-vista

Orquesta la traducción de **una** vista desde VQL local. Lo ejecutas tú (la sesión principal
de Coda); los subagentes entran en pasos concretos y se comunican **solo a
través del ledger** (`ledger/{vista}.md`).

**Argumento:** el nombre de la vista tal como aparece en el VQL local viene en el mensaje del
usuario (ej. `/migrar-vista rv_xxx_yyy_v` o "usa migrar-vista con la vista
rv_xxx_yyy_v"). Si no viene, **pregúntalo antes de empezar**; no lo infieras.

## Antes de empezar

- Lee `producto.yml`. Si tiene valores `TODO`, pide correr `/iniciar-producto`.
- Si `ledger/{vista}.md` ya existe, léelo y **retoma desde su estado** en vez
  de rehacer: `explorado` → paso 2; `ddl_propuesto` → paso 3; etc.
- Crea la lista de tareas con una por paso.

## Pasos

### 1. Explorar — agente `vql-explorer`
Lánzalo (run_agent) con el nombre de la vista. Resultado esperado:
`ledger/{vista}.md` con estado `explorado`, cadena de dependencias, VQL por
nivel y parámetros. Revisa el resumen: si quedaron ramas sin explorar o
archivos no encontrados, muéstraselo al desarrollador antes de seguir.

### 2. Diseñar — agente `tsql-view-architect`
Lánzalo pasándole la ruta del ledger. Resultado: `ddl/{vista}.sql`,
diagnóstico en el ledger y estado `ddl_propuesto`.

### 3. 🛑 Compuerta humana — revisión y despliegue
**Detente.** Presenta al desarrollador:
- el DDL propuesto (ruta `ddl/{vista}.sql`),
- los supuestos y riesgos estáticos sin resolver (si los hay),
- cualquier parámetro que requiera una decisión (qué se expone, qué filtra el reporte).

Dile que revise el DDL y sus supuestos y que, si lo aprueba, **lo despliegue
en Fabric él mismo**. Nunca despliegues ni ejecutes DDL. No hay un paso de
comparación automática con Denodo: el harness solo analiza los archivos VQL
locales. Si quedan decisiones de negocio abiertas, documéntalas en el ledger
como pendientes de resolución humana.

### 4. Cierre
Resume en pocas líneas: estado del ledger, ruta del DDL, supuestos, decisiones
pendientes y la compuerta de revisión/despliegue a cargo del ingeniero. No
indiques un comando de comparación Denodo↔Fabric: ese flujo no forma parte del
harness.

## Reglas

- **Una vista por corrida.** Para un lote, corre el comando por vista; no
  lances todas en paralelo sin que el desarrollador lo pida.
- Ningún agente despliega ni modifica Fabric.
- El ledger es la única fuente de verdad entre agentes.
