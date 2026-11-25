---
name: trs9-preflight
description: Verifica (y con --instalar instala) todo lo necesario para el flujo de transición TRS-9 - Python, uv, dependencias Python del proyecto, fab (fabric-cli), sesión de Azure CLI y fab, Node.js/npx, dnx, driver ODBC y claves del .env. Usar al iniciar cualquier trabajo de documentación de transición TRS-9 o cuando fallen imports, `fab` o `az`.
---

# Preflight TRS-9

```bash
python .coda/skills/trs9-preflight/scripts/preflight.py             # solo verifica (~1 min, `az` es lento)
python .coda/skills/trs9-preflight/scripts/preflight.py --instalar  # + `uv sync` y `uv tool install ms-fabric-cli`
```

- Solo usa la librería estándar, así que corre antes de instalar nada.
- **Instala** únicamente dependencias Python del proyecto y `fab` (vía `uv`); pide
  confirmación al usuario antes de usar `--instalar`.
- **No instala** nada de sistema (Python, uv, Azure CLI, Node.js, .NET, ODBC) ni hace
  `az login`/`fab auth login` (abren el navegador): indica al usuario el paso exacto.
- Estados: `OK`, `FALTA` (obligatorio; exit code 1) y `AVISO` (opcional o dependiente del
  paso, p. ej. ODBC y `.env` solo hacen falta para consultas SQL).
- Del `.env` solo reporta **nombres de claves**, nunca valores.
