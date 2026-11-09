# Patrones base de la migración VQL → T-SQL (Fabric Gold)

> Archivo de la **plantilla** (se actualiza vía git) con patrones comunes para
> traducir VQL a T-SQL. Todos los agentes lo leen antes de traducir una vista.
> Los patrones propios de tu producto van en `patrones-producto.md`.
>
> Cada patrón: **Síntoma → Causa → Regla**. Los campos `Ref` conservan los
> números del catálogo de origen únicamente como identificadores históricos;
> no enlazan a documentación externa. La evidencia específica de cada producto
> debe quedar en su ledger; no se incluyen aquí datos de productos.

---

## A. Parámetros de vista (`USING PARAMETERS`)

T-SQL no tiene parámetros de vista. Clasifica cada parámetro en uno de estos
cuatro patrones **antes** de escribir el DDL.

### P01 — Parámetro disfrazado de columna (eco)
- **Síntoma:** la vista devuelve el propio parámetro como columna de salida
  (mismo nombre o sufijo `_bv`); el reporte filtra por esa columna y luego la
  elimina. La comparación `[col] = param` es una tautología que no filtra.
- **Causa:** Denodo refleja el valor del parámetro en cada fila.
- **Regla:** no asumir que una columna con nombre parecido a un parámetro es
  el filtro real. Revisar el VQL de la report view **y** de la base view; si
  falta alguno, dejar la interpretación pendiente.
- *Ref:* Patrón 1.

### P02 — "Top N" / "últimas N semanas" resuelto con parámetro
- **Síntoma:** la lógica real es `ROW_NUMBER()/DENSE_RANK() ... WHERE NUM <= @param`.
- **Causa:** Denodo/HANA aceptan el parámetro; T-SQL no.
- **Regla:** calcular el rank sobre **todo el histórico** dentro de la vista,
  exponerlo como columna, y mover el filtro al consumidor. Replicar el
  operador exacto: puede ser `NUM <= N OR SEMANA = X`, no un simple `<=`.
- *Ref:* Patrón 2.

### P08 — Variable de wrapper que mapea a una columna ya expuesta
- **Síntoma:** el `USING PARAMETERS` se usa en el WHERE contra una variable
  `ISWRAPPERVARIABLE` de la base view, cuyo `sourcecolumn` es el mismo campo
  físico que otra columna normal del SELECT.
- **Causa:** el parámetro es solo una forma de pasarle a Denodo el valor con
  que filtrar una columna real.
- **Regla:** distinguirlo de P01 revisando el `OUTPUTSCHEMA` del wrapper. Se
  traduce con un filtro normal sobre la columna real (`WHERE col IN (...)`);
  no hace falta ningún mecanismo de parámetro.
- *Ref:* Patrón 8.

### P14 — Parámetro obligatorio (`OBL`) sin columna física detrás
- **Síntoma:** el wrapper declara el parámetro con `extern` y `OBL ONE`; se
  propaga por varios niveles de vistas como "pseudo-columna" y nunca aparece
  en un SELECT final.
- **Causa:** es un *input parameter* propio de la Calculation View de HANA.
  La tabla en Fabric puede estar ya **pre-filtrada** por el valor que se eligió
  al extraer.
- **Regla:** antes de tratarlo como P01 puro, buscar en el VQL si el mismo
  valor semántico es derivable de otra columna. Si el archivo no aporta
  evidencia suficiente, documentar el supuesto y dejarlo pendiente.
- *Ref:* Patrón 14.

---

## B. Cambios de comportamiento y lógica oculta

### P05 — Cambio de comportamiento por reinterpretación
- **Síntoma:** una vista "equivalente" devuelve distinto conjunto de filas
  (ej. un `CROSS JOIN` sin condición convertido en `INNER JOIN` con condición
  de fecha).
- **Causa:** quien migró reinterpretó la lógica sin notarlo. No es bug de sintaxis.
- **Regla:** comparar comportamiento, no solo sintaxis. Señalar toda
  diferencia y **nunca decidir si es aceptable**: es decisión del dueño de
  negocio, con evidencia (qué cambia y con qué datos).
- *Ref:* Patrón 5.

### P10 — Lógica de negocio dentro de la Calculation View de HANA
- **Síntoma:** la `DESCRIPTION` de la vista habla de condiciones ("fecha
  máxima de corte", "excluye nulos") que ningún WHERE del VQL aplica;
  columnas agregadas (contadores, rankings) aparecen sin cálculo visible.
- **Causa:** la base view es un `WRAPPER JDBC` puro sobre una Calculation View
  de `_SYS_BIC`; la lógica vive en HANA y el VQL no la contiene.
- **Regla:** un pass-through solo representa la misma lógica si la ingesta
  **materializó el resultado** de la Calculation View. No reconstruir la lógica
  por intuición: documentar la incertidumbre y, si es necesario, consultar
  únicamente la capa disponible en Fabric en modo solo lectura.
- *Ref:* Patrón 10.

### P09 — Semi-join `IN (SELECT DISTINCT ...)` degradado a JOIN
- **Riesgo:** conteos y sumas pueden inflarse aunque el reporte parezca funcionar.
- **Causa:** un `JOIN` sin deduplicar multiplica filas; un semi-join no. Con
  varios predicados en el subquery, deben evaluarse **sobre la misma fila**.
  En SQL, `X IN (lista)` con `X IS NULL` excluye la fila.
- **Regla:** traducir el semi-join como `EXISTS`/`IN`, no como `JOIN`. Si hay
  que reensamblarlo en otra capa, deduplicar y quitar nulos de la lista.
- *Ref:* Patrón 9.

### P06 — Columnas de auditoría hardcodeadas
- **Síntoma:** `Origen = 'Denodo'` y similares quedan desactualizadas.
- **Regla:** actualizarlas al nuevo origen, pero solo tras confirmar que no se
  usan en medidas o filtros del reporte.
- *Ref:* Patrón 6.

---

## C. Semántica de funciones y tipos

### P22 — Collation sensible a mayúsculas rompe JOIN sobre GUID/texto
- **Riesgo:** un JOIN sobre GUID/texto puede no coincidir por diferencias de mayúsculas y collation.
- **Causa:** un lado guarda GUIDs en mayúsculas y el otro en minúsculas; el
  Warehouse compara sensible a mayúsculas.
- **Regla:** `LOWER()` en ambos lados del JOIN (y en filtros de igualdad de
  texto) cuando el origen era case-insensitive.
- *Ref:* Patrón 22.

### P23 — `DATEDIFF(DAY, ...)` ≠ `getdaysbetween()`
- **Riesgo:** la columna "días entre" puede diferir ±1 si se traduce el cambio de fecha como días completos transcurridos.
- **Causa:** con timestamps con hora real, Denodo trunca el tiempo transcurrido
  a días completos; `DATEDIFF(DAY)` cuenta cambios de fecha.
- **Regla:** replicar el truncamiento (diferencia en horas/minutos dividida y
  truncada, o ajustar según la hora) a partir de la semántica VQL. Registrar
  como riesgo de traducción que no se ha validado contra resultados de origen.
- *Ref:* Patrón 23.

### P25 — Columna con `GETDATE()`/`CURRENT_TIMESTAMP` calculada en vivo
- **Riesgo:** una columna de fecha/hora de "actualización" calculada al vuelo no es reproducible entre ejecuciones.
- **Causa:** depende del instante exacto de cada consulta; nunca coincide.
- **Regla:** dos consultas pueden producir valores distintos por el instante
  de ejecución. Documentar la columna como no determinista; si debe ser fecha
  de carga, usar una columna física y no `GETDATE()`.
- *Ref:* Patrón 25.

### P17 / P28 — Fechas como `bigint` `YYYYMMDD` o texto crudo
- **Síntoma:** filtros de rango raros, errores de tipo que **solo aparecen en
  refresh completo** del modelo y no en el preview del reporte.
- **Causa:** columna de "fecha" que en la fuente es `bigint`/texto `YYYYMMDD`
  mientras Denodo la exponía ya como fecha formateada.
- **Regla:** convertir explícitamente en el DDL (`TRY_CONVERT(DATE, ..., 112)`),
  y alinear el tipo con lo que el modelo del reporte espera.
- *Ref:* Patrones 17 y 28.

### P31 — Corrimiento sistemático de −1 día en fechas HANA
- **Riesgo:** las conversiones de timestamp a date pueden provocar un corrimiento sistemático de fecha por zona horaria.
- **Causa:** `TIMESTAMP` en Bronze + `DATE` en el DDL de Silver +
  `spark.sql.session.timeZone` mal alcanzado en la ingesta.
- **Regla:** inspeccionar la conversión de zona horaria y los tipos entre
  ingesta y DDL. El posible arreglo puede estar en Silver/ingesta, no en Gold;
  sin evidencia local o de Fabric, documentar como riesgo y escalar.
- *Ref:* Patrón 31.

---

## Cómo se agrega un patrón

1. El agente (o el desarrollador) lo **propone** en la sección "¿Patrón nuevo?"
   del ledger: síntoma, causa raíz, regla y caso real (vista y evidencia).
2. El desarrollador lo confirma.
3. Si es específico del producto → `patrones-producto.md`. Si es general →
   se propone al repo de la plantilla para que lo reciban todos los productos.
