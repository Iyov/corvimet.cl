# AGENTS.md

Instrucciones para agentes de código (Claude Code, Codex, Cursor, Copilot, etc.).

## Proyecto
Nuevo sitio y tienda online de corvimet.cl en Cloudflare: páginas estáticas endurecidas (fase 0, terminada), más un Worker con D1, R2, Access y la API de Flow para el mantenedor de productos y la venta online (etapas 4 y 5). Lee primero:
- [docs/04-producto-y-mejoras.md](docs/04-producto-y-mejoras.md): qué se construye y por qué (criterios de aceptación por etapa).
- [docs/SSD.md](docs/SSD.md): requisitos (RF, RA, RT, RS, RM), arquitectura, modelo de datos, rutas y seguridad.
- [docs/05-despliegue-y-entornos.md](docs/05-despliegue-y-entornos.md): entornos, secretos y despliegue.
- [MEMORY.md](MEMORY.md): decisiones y estado.

## Pipeline de la fase 0 (no saltarse etapas)
`tools/mirror.py` (corvimet.cl → `site/`) → `tools/harden.py` (`site/` → `public/`) → `tools/verify.py` → navegador.

## Reglas de la tienda y el mantenedor (etapas 4 y 5)
- **Precio:** una sola función de precio vigente (oferta en ventana `America/Santiago`) usada por las páginas, el carrito y el checkout. El servidor **siempre** recalcula; nunca aceptar precios del cliente.
- **Pagos:** se marcan como pagados solo tras `urlConfirmation` + `payment/getStatus` firmados y con monto igual; idempotencia por `commerce_order`. Nunca confiar en la redirección de retorno.
- **Secretos:** `FLOW_API_KEY`, `FLOW_SECRET_KEY`, `TURNSTILE_SECRET` solo vía `wrangler secret`. Nunca en código, `wrangler.jsonc`, logs ni tests. Local en `.dev.vars` (gitignored).
- **Admin:** toda ruta `/api/admin/*` valida el JWT de Cloudflare Access (`aud` e `iss`) y `Origin`; cada escritura deja un registro en `audit_log`.
- **Cabeceras:** `_headers` no se aplica a las respuestas generadas por el Worker; usar el middleware común de cabeceras.
- **D1:** cambios de esquema solo con migraciones nuevas en `migrations/` (nunca editar una ya aplicada). Aplicar en preview antes que en producción.
- **SEO:** no cambiar URL públicas sin una redirección 301 (tabla `redirects` o `_redirects`).
- **Pruebas:** Vitest con `@cloudflare/vitest-pool-workers`; obligatorias para precio vigente, firma Flow, idempotencia, RUT y JWT.

## Reglas
- **Autoría:** el único autor de este repo es Francisco Barrientos (`francisco.barrientos@usach.cl`, cuenta GitHub `Iyov`). Ningún agente o herramienta de IA (Claude, Claude Code, Codex, Copilot, etc.) puede aparecer como autor, coautor ni contribuidor: no se usan trailers `Co-Authored-By`, líneas "Generated with…" en commits o PRs, ni identidades `noreply@anthropic.com` o similares.
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
