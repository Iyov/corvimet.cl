# AGENTS.md

Instrucciones para agentes de código (Claude Code, Codex, Cursor, Copilot, etc.).

## Proyecto
Copia estática de corvimet.cl (WordPress, WooCommerce y Elementor) servida por Cloudflare Workers Static Assets. Diseño completo en [docs/SSD.md](docs/SSD.md); decisiones y estado en [MEMORY.md](MEMORY.md).

## Pipeline (no saltarse etapas)
`tools/mirror.py` (corvimet.cl → `site/`) → `tools/harden.py` (`site/` → `public/`) → `tools/verify.py` → navegador.

## Reglas
- **No editar `public/` a mano.** Se regenera completo con `harden.py`. Los cambios van en `tools/harden.py` o en `config/`.
- **Nunca** agregar a la CSP `'unsafe-inline'` en scripts, `'unsafe-eval'` ni hosts de terceros sin actualizar SSD §4.2 y §6 con la justificación.
- Todo JS o CSS nuevo va en archivo externo. Nada de `<script>`, `<style>` ni `on*=` en línea.
- `_headers`: máximo 100 reglas y 2.000 caracteres por línea. No definir `Cache-Control` en `/*` (se concatena).
- Antes de terminar un cambio: `python tools/harden.py && python tools/verify.py` debe dar 0 errores.
- Verificación en navegador con **Chrome Canary** (`tools/check-browser.mjs`, su valor por defecto) contra `tools/serve.py`.
- No commitear `site/`, `screenshots/` ni `.wrangler/`. No commitear secretos (tokens de Cloudflare van en el panel o en los secrets de GitHub).
- El crawl respeta robots.txt y pausa 150 ms entre peticiones; no bajar ese valor.
- En Git Bash (Windows), usar `MSYS_NO_PATHCONV=1` al pasar rutas `/...` a Node.

## Comandos
```bash
pip install -r requirements.txt
python tools/harden.py && python tools/verify.py
python tools/serve.py 8765
MSYS_NO_PATHCONV=1 node tools/check-browser.mjs http://127.0.0.1:8765 / /store/ /producto/molde-poste/
```
