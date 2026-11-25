# BacklogCreator

Agente para crear los **Product Backlog Items** estándar (HU 01–HU 09) de un
nuevo **Producto de Datos** en Azure DevOps, usando el MCP de Azure DevOps de Coda.

> **Origen:** este agente fue migrado desde GitHub Copilot (`.github/`).
> La lógica es la misma; la invocación ahora usa el MCP de azure-devops.

## Estructura

| Ruta | Qué es |
|---|---|
| `.coda/skills/replicar-backlog/SKILL.md` | Skill de Coda: flujo completo para crear los 9 PBIs |
| `.coda/mcp.json` | MCP de Azure DevOps (org `ecopetrolad`, auth interactiva) — ya configurado |
| `BacklogTemplates/data_product_backlog.json` | Plantilla JSON con las 9 HUs (title, description HTML, tags, acceptanceCriteria HTML) |
| `BacklogTemplates/replicador_backlogs.instructions.md` | Instrucción original (referencia histórica) |
| `.github/` | Configuración original de Copilot (referencia histórica) |

## Uso

En una sesión de Coda abierta en esta carpeta (o en la raíz del repo), invoca:

```
/replicar-backlog
```

> **Si copiaste esta carpeta a otro lugar:** abre la sesión de Coda dentro de
> ella (o reiníciala) para que Cargue el `.coda/mcp.json` y la skill. El MCP
> pedirá login interactivo la primera vez que se use.

La skill te pedirá:

1. Nombre del Producto de Datos (`{{ProductName}}`)
2. Dominio (`{{DomainName}}`)
3. Azure DevOps Project
4. Area Path
5. Iteration Path
6. Assignee (opcional)
7. Tags adicionales (opcional)

Luego hace validación previa (proyecto y tipo de work item), muestra un
**preview** de los 9 items y **solo con tu confirmación explícita** los crea
en Azure DevOps vía MCP, reportando IDs y URLs al final.

## Mejoras respecto a la versión de Copilot

- **Compuerta humana obligatoria**: preview (dry-run) antes de crear nada.
- **Validación previa**: verifica que el proyecto y el tipo "Product Backlog Item"
  existen antes de intentar crear.
- **Manejo de errores por item**: si uno falla, continúa con los demás y reporta
  el error al final (antes un fallo podía cortar todo el flujo).
- **Reporte final estructurado**: IDs + títulos + URLs de verificación.
- **Ruta de plantilla relativa al repo** (antes estaba hardcodeada a una ruta
  absoluta de otra carpeta `Transicion`).
- **Reglas explícitas**: no inventar valores, no publicar sin pedido explícito.

## Estado

⚠️ **No se ha publicado nada en ningún backlog todavía.** La estructura está
lista; la creación real de work items ocurre solo cuando alguien corre
`/replicar-backlog` y confirma el preview.
