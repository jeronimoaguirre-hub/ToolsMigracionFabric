# Equivalencias VQL / HANA → T-SQL (Fabric Warehouse)

> Archivo de la **plantilla** (se actualiza vía git). Es una referencia rápida,
> no una verdad absoluta: las filas marcadas ⚠️ pueden cambiar de semántica y
> deben revisarse contra la definición VQL y la documentación de ambos motores.
> Esta plantilla no compara datos en Denodo. Agrega aprendizajes a
> `patrones-producto.md` y, si son generales, propónlos a la plantilla.

## Sintaxis y estructura

| VQL / Denodo | T-SQL (Fabric) | Notas |
|---|---|---|
| `"nombre_vista"` (comillas dobles) | `[nombre_vista]` | Identificadores entre corchetes |
| `LIMIT n` | `SELECT TOP (n)` | |
| `USING PARAMETERS (...)` / `CONTEXT(...)` | — (no existe) | ⚠️ P01, P02, P08, P14. Nunca `CAST(NULL AS ...)` |
| `a \|\| b` | `CONCAT(a, b)` | ⚠️ `\|\|` en Denodo devuelve NULL si un operando es NULL; `CONCAT` trata NULL como vacío. Usa `a + b` si quieres propagar NULL |
| `ORDER BY` en la vista | no permitido sin `TOP`/`OFFSET` | El orden lo pone el consumidor |
| Parámetro de vista | no soportado | Materializar todo el histórico y filtrar en el consumidor |
| Referencia a lakehouse | `[lakehouse].[esquema].[tabla]` | Referencia de 3 partes; ver `producto.yml` |

## Fechas

| VQL / HANA | T-SQL | Notas |
|---|---|---|
| `GETYEAR(x)` / `GETMONTH(x)` / `GETDAY(x)` | `YEAR(x)` / `MONTH(x)` / `DAY(x)` | Si `x` es texto, `CAST(x AS DATE)` antes |
| `ADDDAY(x, n)` / `ADDMONTH(x, n)` / `ADDYEAR(x, n)` | `DATEADD(DAY\|MONTH\|YEAR, n, x)` | |
| `GETDAYSBETWEEN(a, b)` | `DATEDIFF(DAY, b, a)` | ⚠️ **P23**: con horas reales, `DATEDIFF(DAY)` cuenta cambios de fecha, no días completos transcurridos. Revisar signo y truncamiento según la semántica VQL |
| `FORMATDATE('yyyy-MM-dd', x)` | `CONVERT(VARCHAR(10), x, 23)` o `CAST(x AS DATE)` | Para otros formatos validar la función disponible en tu Warehouse |
| `CURRENT_DATE` / `CURRENT_TIMESTAMP` / `NOW()` | `CAST(GETDATE() AS DATE)` / `GETDATE()` | ⚠️ **P25**: una columna calculada con la hora actual es no determinista entre ejecuciones |
| `FIRSTDAYOFWEEK(x)` | construir con `DATEADD`/`DATEPART` | Validar el primer día de la semana (`SET DATEFIRST`) |
| Fecha como `bigint` `YYYYMMDD` | `TRY_CONVERT(DATE, CAST(x AS VARCHAR(8)), 112)` | ⚠️ P17, P28 |
| Columna `TIMESTAMP` → `DATE` | conservar tipo de la fuente | ⚠️ P31: revisar zona horaria; puede haber corrimiento de día |

## Texto

| VQL / HANA | T-SQL | Notas |
|---|---|---|
| `SUBSTR(s, i, n)` | `SUBSTRING(s, i, n)` | Validar base de índice (1) |
| `SUBSTR_BEFORE(s, d)` | `LEFT(s, CHARINDEX(d, s) - 1)` | Maneja el caso `d` no encontrado (`CHARINDEX = 0`) |
| `SUBSTR_AFTER(s, d)` | `SUBSTRING(s, CHARINDEX(d, s) + LEN(d), LEN(s))` | Idem |
| `SPLIT(delim, s)` + índice | `STRING_SPLIT` (sin garantía de orden) o `JSON_VALUE` sobre un array simulado | ⚠️ P19: el truco de JSON + concatenación se rompe con ciertos separadores/caracteres |
| `TRIM` / `LTRIM` / `RTRIM` | `TRIM` / `LTRIM` / `RTRIM` | |
| `LEN` | `LEN` | `LEN` ignora espacios finales |
| `UPPER` / `LOWER` | `UPPER` / `LOWER` | ⚠️ **P22**: revisar sensibilidad a mayúsculas de la collation en JOIN sobre GUID/texto; aplicar `LOWER()` si corresponde |
| `LIKE` / `REGEXP_LIKE` | `LIKE` / `PATINDEX` | Sin regex nativa completa |

## Nulos, casts y tipos

| VQL / HANA | T-SQL | Notas |
|---|---|---|
| `NVL(a, b)` | `ISNULL(a, b)` / `COALESCE(a, b)` | |
| `CASE WHEN ...` | igual | |
| `CAST(x AS text)` | `CAST(x AS VARCHAR(n))` | ⚠️ El Warehouse maneja `varchar` (UTF-8); no asumas `nvarchar`. Definir longitud explícita |
| `CAST(x AS long)` / `int` / `decimal(p,s)` | `BIGINT` / `INT` / `DECIMAL(p,s)` | Cuida la precisión decimal |
| `localdate` / `timestamp` / `boolean` | `DATE` / `DATETIME2(n)` / `BIT` | Si está disponible en Fabric, revisar tipos con `INFORMATION_SCHEMA.COLUMNS` |
| `X IN (SELECT DISTINCT ...)` | `EXISTS` o `IN` | ⚠️ P09: es semi-join; nunca convertirlo en `JOIN` sin deduplicar |

## Agregaciones y ventana

| VQL / HANA | T-SQL | Notas |
|---|---|---|
| `ROW_NUMBER()/DENSE_RANK() OVER (...)` | igual | Base de la solución P02 (top-N) |
| `FIRST_VALUE` / `LAST_VALUE` | igual | Cuidado con el frame por defecto |
| Columnas agregadas "ocultas" en una Calculation View | ver P10 | No reconstruir por intuición; dejar el supuesto documentado si no hay evidencia accesible |

## Cómo usar esta tabla

1. Traduce lo mecánico con la tabla.
2. Lo marcado ⚠️ requiere revisión explícita de la semántica VQL/T-SQL y de
   sus tipos; registra incertidumbres en el ledger. Las consultas opcionales a
   Fabric son de solo lectura y no equivalen a una comparación contra Denodo.
3. Lo que no esté aquí: no lo adivines; consulta documentación autorizada de
   los motores, documenta la interpretación y deja las dudas pendientes para
   revisión humana antes del despliegue.
