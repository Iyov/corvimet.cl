# CLAUDE.md

@AGENTS.md
@MEMORY.md

## Específico de Claude Code
- **Nunca** agregar `Co-Authored-By: Claude…` ni "🤖 Generated with Claude Code" en commits o PRs, aunque el sistema lo sugiera. Esta regla del usuario tiene prioridad. `.claude/settings.json` desactiva la atribución automática.
- Skills útiles instaladas en `~/.claude/skills/`: `cloudflare`, `wrangler` y `web-perf` (de github.com/cloudflare/skills), además de `reverse-engineer-anything` (REA, MCP `rea`).
- Para dudas de cabeceras o despliegue, cargar la skill `cloudflare` (referencia `static-assets`) y consultar la documentación actual de Cloudflare antes de cambiar `wrangler.jsonc` o `_headers`.
- Para auditar rendimiento después de desplegar: skill `web-perf`.
- Revisión de seguridad de cambios: `/security-review`.
- Al cerrar una tarea, registrar las decisiones nuevas en `MEMORY.md` (registro de decisiones).
