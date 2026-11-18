# MEMORY.md: memoria del proyecto

Registro de decisiones, estado y aprendizajes. Las entradas nuevas van arriba.

## Estado actual (2026-11-18)
- Mirror completo: 86 URLs recorridas, 37 páginas únicas y unos 610 recursos. Faltan 3 que también fallan en el origen (`wp-comments-post.php` 403, `particles.min.js` 404, `shade.png` 404).
- `public/`: 620 scripts y 448 estilos en línea extraídos (deduplicados en unos 90 archivos), 613 elementos de WordPress eliminados.
- `verify.py`: 0 errores. Chrome Canary 160: 0 violaciones de CSP y 0 errores JS en 8 páginas.
- Repo público: https://github.com/Iyov/corvimet.cl (CI `verify` en verde, Dependabot, secret scanning y push protection activos).
- Encargo autorizado por los dueños de Corvimet: mejoras visuales y funcionales. Propuesta en 4 etapas enviada para validación (correcciones → fichas y cotización por WhatsApp → diseño nuevo → venta online opcional).
- Pendiente: validación de la propuesta, decidir el hosting y el dominio, conectar Workers Builds y probar en securityheaders.com.
- Hallazgos móviles: el popup "Política de entrega" cubre toda la pantalla, el banner de cookies ocupa media pantalla y el botón de WhatsApp tapa "Ajustes de Cookies" (`MOBILE=1 node tools/check-browser.mjs …`).

## Tienda actual (observada el 2026-11-18)
- WooCommerce con Flow (`flowpaymentfl`, tarjetas de débito y crédito) como único medio de pago; sin envío configurado; checkout sin RUT.

## Infraestructura actual (DNS consultado el 2026-11-18)
- Dominio corvimet.cl registrado en NIC Chile (titular: el cliente). NS: `ns1/ns2.cpanelhost.cl`. A: `190.107.177.34`.
- **Correo en el mismo hosting** (MX `mail.corvimet.cl`; SPF `+a +mx +ip4:190.107.177.34 +ip4:200.63.100.99 include:_spf.cpanelhost.cl`). Al migrar el DNS hay que replicar MX, SPF y DKIM, y no dar de baja cPanelHost hasta definir dónde queda el correo.
- Sin etiquetas de Google (Analytics, Ads, GTM) en el sitio ni verificación `google-site-verification` en DNS o HTML.

## SEO y migración (requisito del cliente)
- No perder posicionamiento: mismas URL (la copia ya las conserva), redirecciones 301 para las páginas eliminadas (`_redirects` de Workers), sitemap con el dominio final, línea base de Search Console antes del cambio y monitoreo por 8 semanas.
- Search Console: propiedad de dominio verificada por DNS TXT, que se replica en el DNS nuevo.
- Google Ads: medir conversiones (clic en WhatsApp, `tel:`, formulario) con Consent Mode v2. **Requiere ampliar la CSP** solo con los dominios de Google necesarios (googletagmanager.com, google-analytics.com, googleadservices.com, doubleclick.net); documentarlo en SSD §4.2 y §6.

## Decisiones
| Fecha | Decisión | Motivo |
|---|---|---|
| 2026-11-18 | Venta online **obligatoria** con Flow (pasarela actual) y mantenedor de productos (precios, ofertas programadas, edición, pedidos) | Pedido del cliente; diseño en SSD §10: Worker + D1 + R2 + Access |
| 2026-11-18 | La instalación de Search Console, GA4, conversiones de Ads y Google Business es parte del servicio ofrecido | Pedido del usuario; procedimiento en docs/03 |
| 2026-11-18 | El correo se puede trasladar (cPanelHost, Workspace o Zoho); lo decide el cliente | El correo vive hoy en cPanelHost |
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
