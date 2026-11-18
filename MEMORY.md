# MEMORY.md: memoria del proyecto

Registro de decisiones, estado y aprendizajes. Las entradas nuevas van arriba.

## Estado actual (2026-11-18)
- Mirror completo: 86 URLs recorridas, 37 páginas únicas y unos 610 recursos. Faltan 3 que también fallan en el origen (`wp-comments-post.php` 403, `particles.min.js` 404, `shade.png` 404).
- `public/`: 620 scripts y 448 estilos en línea extraídos (deduplicados en unos 90 archivos), 613 elementos de WordPress eliminados.
- `verify.py`: 0 errores. Chrome Canary 160: 0 violaciones de CSP y 0 errores JS en 8 páginas.
- Pendiente: crear el repo en GitHub, conectar Workers Builds, definir el dominio y probar en securityheaders.com.

## Decisiones
| Fecha | Decisión | Motivo |
|---|---|---|
| 2026-11-18 | Hosting en Cloudflare Workers Static Assets | GitHub Pages no permite cabeceras; Cloudflare recomienda Workers sobre Pages |
| 2026-11-18 | Extraer JS y CSS en línea en lugar de usar hashes en la CSP | Límite de 2.000 caracteres por línea en `_headers` |
| 2026-11-18 | Verificación en navegador con Chrome Canary | Pedido del usuario: motor más reciente |
| 2026-11-18 | Excluir `/author/` | Revela el usuario `admin` del WordPress real |
| 2026-11-18 | Eliminar `wc-cart-fragments`, emojis y speculation rules | Fallan sin backend o cargan recursos de terceros |
| 2026-11-18 | Sin COEP ni Trusted Types | Rompen el iframe de Maps y jQuery/Elementor (ver SSD §4.2) |

## Aprendizajes
- El mirror guardó `font.woff2?5.11.0` como `font_<hash>.woff2`; `harden.py` también lo publica con el nombre original.
- Durante el mirror quedaron URLs `https:/_ext/...` (con una sola barra); `strip_domain()` las normaliza.
- Git Bash convierte `/ruta` en `C:/Program Files/Git/ruta` al pasarla a Node: usar `MSYS_NO_PATHCONV=1`.
- La extensión Claude in Chrome no llega a servidores en localhost en este equipo; para verificar se usa `check-browser.mjs` (CDP).
- El esquema de `capture_browser_scenario` de REA es estricto (requiere `step_id`, acciones `goto`/`wait_for_timeout`…); para este caso es más simple CDP directo.
