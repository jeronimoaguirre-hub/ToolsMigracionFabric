# Ledger de traducción: {nombre_vista}

## Estado
<!-- explorado | ddl_propuesto | desplegado_por_ingeniero | revision_estatica_completada | pendiente_decision -->
explorado

## Cadena de dependencias (report view → origen descrito en el VQL)
- rv_... (report view)
  - bv_... (base view)
    - origen físico descrito en el archivo VQL (Calculation View / tabla)

## Archivos VQL locales revisados
- `denodo-vql/...`

## VQL completa por nivel
### report view: rv_...
```sql
[VQL tal cual se encontró en el archivo local]
```

### base view: bv_...
```sql
[VQL tal cual se encontró en el archivo local]
```

## Parámetros detectados
| Parámetro | Tipo declarado | Nivel donde aparece | Uso en el WHERE (cita textual) | Tratamiento propuesto |
|---|---|---|---|---|

## Notas de exploración
[archivos no encontrados, referencias circulares, columnas eco, lógica oculta…]

## DDL existente en Fabric (si se consultó)
```sql
[o "no consultado" o definición obtenida de Fabric en modo lectura]
```

## Diagnóstico de traducción
[qué se tradujo, supuestos, diferencias potenciales respecto a la semántica expresada en VQL]

## DDL propuesto
Archivo: `ddl/{vista}.sql`
```sql
[copia del DDL]
```

## Decisiones pendientes
[lista explícita con evidencia y responsable, o "ninguna detectada"]

## Despliegue humano
- Desplegado por / fecha:
- Notas:

## Revisión estática
- Alcance y archivos revisados:
- Hallazgos:
- Consultas Fabric de solo lectura ejecutadas (query exacta y resultado), o "no consultadas":
- Límites: no se ejecutó comparación de resultados contra Denodo.

## ¿Patrón nuevo?
[sí — descríbelo | no]
