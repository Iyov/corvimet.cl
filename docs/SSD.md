# SSD: Especificación y Diseño del Sistema
**Proyecto:** Copia estática y endurecida de corvimet.cl
**Versión:** 1.0 · **Fecha:** 2026-11-18

---

## 1. Propósito y alcance
Construir y publicar, desde este repositorio de GitHub, una réplica fiel del sitio WordPress https://corvimet.cl/ como **sitio estático** servido por **Cloudflare Workers Static Assets**, con cabeceras de seguridad actuales.

**Dentro del alcance:** todas las páginas públicas (portada, tienda, 18 productos, 3 categorías, páginas institucionales y de demo), sus recursos (CSS, JS, imágenes y fuentes), el comportamiento de cliente (sliders, popups de Elementor, menú, banner de cookies, botón de WhatsApp), la 404 y las políticas de seguridad.

**Fuera del alcance:** funciones que requieren PHP o base de datos: carrito, checkout, cuentas, envío de formularios y búsqueda (ver §8).

## 2. Contexto del sistema de origen
Ver [01-documentacion-sitio.md](01-documentacion-sitio.md). Resumen: WordPress 7.1.4, WooCommerce 5.4.4, tema Astra 2.6.2, Elementor y Elementor Pro, alojado en Apache con LiteSpeed Cache.

## 3. Requisitos

### 3.1 Funcionales
| ID | Requisito | Verificación |
|---|---|---|
| RF-01 | Toda URL pública del sitemap existe en la copia con la misma ruta | `tools/verify.py` y crawl |
| RF-02 | Las páginas se ven igual que el original (layout, fuentes, imágenes) | Capturas con `tools/check-browser.mjs` |
| RF-03 | El JS de cliente funciona (popups, slider, menú móvil, cookies) | Chrome Canary sin errores JS |
| RF-04 | Una URL inexistente devuelve la 404 original con estado 404 | `not_found_handling: 404-page` |
| RF-05 | El sitio se despliega automáticamente al hacer push a `main` | Cloudflare Workers Builds |
| RF-06 | La copia puede regenerarse desde cero con un comando por etapa | `mirror.py` → `harden.py` |

### 3.2 No funcionales (seguridad)
| ID | Requisito |
|---|---|
| RS-01 | CSP estricta: `script-src 'self'`, **sin** `'unsafe-inline'` ni `'unsafe-eval'` en scripts |
| RS-02 | Ningún `<script>`, `<style>` ni handler `on*` en línea en el HTML publicado |
| RS-03 | Ningún subrecurso de terceros (fuentes e imágenes auto-alojadas); solo el iframe de Google Maps está permitido |
| RS-04 | HSTS de 2 años con `includeSubDomains` y `preload` |
| RS-05 | Aislamiento: COOP `same-origin`, CORP `same-origin`, `Origin-Agent-Cluster`, `frame-ancestors 'none'` |
| RS-06 | Permissions-Policy que niega todas las APIs sensibles |
| RS-07 | Sin huellas de WordPress (`generator`, `wp-json`, `xmlrpc`, `EditURI`) ni página `/author/` |
| RS-08 | `/.well-known/security.txt` (RFC 9116) con `Expires` vigente |
| RS-09 | CI con permisos mínimos y Actions fijadas por SHA |
| RS-10 | Sin secretos en el repositorio |

### 3.3 No funcionales (otros)
- **Rendimiento:** recursos con nombre por hash, cacheables como `immutable` por 1 año; recursos de temas y plugins por 7 días.
- **Portabilidad:** Python 3.11+ y Node 22+ (solo para la verificación en navegador), sin dependencias npm.

## 4. Arquitectura

```
                 ┌─────────────┐  mirror.py   ┌────────┐  harden.py   ┌──────────┐
 corvimet.cl ───►│  crawler    │─────────────►│ site/  │─────────────►│ public/  │
 (WordPress)     └─────────────┘  (en bruto,  └────────┘  (endurecido, └────┬─────┘
                                   gitignored)              versionado)     │ git push
                                                                            ▼
                       verify.py + check-browser.mjs  ◄── GitHub Actions ── GitHub
                                                                            │
                                                         Workers Builds     ▼
                                                  Cloudflare Workers Static Assets
                                                  (_headers, 404-page, auto-trailing-slash)
```

### 4.1 Componentes
| Componente | Archivo | Responsabilidad |
|---|---|---|
| Crawler | `tools/mirror.py` | Recorre sitemaps y enlaces y descarga páginas y recursos (incluye `url()` en CSS, `srcset`, JSON de Elementor y Google Fonts) en `site/` |
| Endurecedor | `tools/harden.py` | Genera `public/`: extrae JS y CSS en línea, quita huellas de WP, localiza recursos de terceros, copia `config/*` |
| Configuración | `config/_headers`, `config/robots.txt`, `config/security.txt` | Fuente editable de cabeceras y archivos públicos |
| Servidor local | `tools/serve.py` | Imita Workers Static Assets (aplica `_headers` y sirve la 404) |
| Verificación estática | `tools/verify.py` | Comprueba RS-01 a RS-03 y RS-07, referencias rotas y límites de `_headers` |
| Verificación en navegador | `tools/check-browser.mjs` | Chrome Canary headless vía CDP: violaciones de CSP, errores JS, 4xx y capturas |
| Despliegue | `wrangler.jsonc` | Worker sin código, solo assets |

### 4.2 Decisiones de diseño
| # | Decisión | Alternativas descartadas | Motivo |
|---|---|---|---|
| D1 | Mirror estático | Migrar WordPress | No hay acceso al hosting; un sitio estático elimina la superficie de ataque de PHP |
| D2 | Workers Static Assets | GitHub Pages, Cloudflare Pages | GitHub Pages no permite cabeceras HTTP (CSP y HSTS reales). Cloudflare recomienda Workers en lugar de Pages para proyectos nuevos |
| D3 | Extraer JS y CSS en línea a archivos con nombre por hash | CSP con hashes o nonces | `_headers` limita cada línea a 2.000 caracteres, y hay más de 600 scripts en línea. Los nonces requieren un servidor dinámico |
| D4 | `style-src-attr 'unsafe-inline'` | Eliminar todos los `style=""` | Elementor y WooCommerce generan cientos de estilos en atributos. El riesgo de inyección vía estilos en atributos es bajo y el resto de la CSP sigue estricto |
| D5 | Sin COEP | `require-corp` o `credentialless` | Rompería el iframe de Google Maps |
| D6 | Sin Trusted Types | `require-trusted-types-for 'script'` | jQuery 3 y Elementor escriben `innerHTML`; queda como mejora futura (§9) |
| D7 | Excluir `/author/` | Copiarlo | Revela el usuario `admin` del WordPress real |
| D8 | Eliminar `wc-cart-fragments`, emojis de `s.w.org` y speculation rules | Mantenerlos | Hacen peticiones AJAX o de terceros que fallan en un sitio estático o violan RS-03 |

## 5. Diseño de datos y rutas
- `site/<ruta>/index.html` corresponde a `https://corvimet.cl/<ruta>/`
- Recursos de terceros: `/_ext/<host>/<ruta>`
- Queries significativas: `nombre_<md5-8>.ext`; `?ver=` se ignora. Si falta el nombre original, también se publica sin hash.
- JS y CSS extraídos: `/assets/inline/<sha256-20>.{js,css}`, deduplicados entre páginas.

## 6. Diseño de seguridad
Cabeceras en `config/_headers` (copiadas a `public/_headers`):

| Cabecera | Valor | Amenaza mitigada |
|---|---|---|
| Content-Security-Policy | `default-src 'none'; script-src 'self'; style-src-elem 'self'; style-src-attr 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; frame-src maps.google.com www.google.com; form-action 'self'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; upgrade-insecure-requests` | XSS, inyección de recursos, exfiltración, clickjacking |
| Strict-Transport-Security | `max-age=63072000; includeSubDomains; preload` | Downgrade y SSL stripping |
| X-Content-Type-Options | `nosniff` | MIME sniffing |
| X-Frame-Options | `DENY` | Clickjacking (navegadores antiguos) |
| Referrer-Policy | `strict-origin-when-cross-origin` | Filtración de URLs |
| Permissions-Policy | todas `()` salvo `fullscreen=(self)` | Abuso de APIs del navegador |
| Cross-Origin-Opener-Policy | `same-origin` | XS-Leaks, ataques de tipo Spectre entre ventanas |
| Cross-Origin-Resource-Policy | `same-origin` | Inclusión de recursos desde otros orígenes |
| Origin-Agent-Cluster | `?1` | Aislamiento de proceso por origen |
| X-Permitted-Cross-Domain-Policies | `none` | Políticas de Flash y PDF |

Límites de Cloudflare: 100 reglas y 2.000 caracteres por línea (`verify.py` los comprueba).

**Configuración recomendada en el panel de Cloudflare** (no se versiona): SSL "Full (strict)", TLS mínimo 1.2, TLS 1.3, Always Use HTTPS, HSTS desde el panel solo si el dominio es propio, DNSSEC, Bot Fight Mode y WAF Managed Rules.

## 7. Verificación
1. `python tools/verify.py`: 0 errores (estado actual: 37 páginas, 0 errores).
2. `python tools/serve.py 8765` y `node tools/check-browser.mjs http://127.0.0.1:8765 / /store/ ...`: 0 violaciones de CSP y 0 errores JS en Chrome Canary 160.
3. Después del despliegue: revisar en https://securityheaders.com y https://observatory.mozilla.org (objetivo: A+).

## 8. Limitaciones
| Función | Estado en la copia | Reemplazo sugerido |
|---|---|---|
| Añadir al carrito, carrito y checkout | Se ve la interfaz, pero la acción no se completa | Botón de WhatsApp o mailto por producto |
| Formularios WPForms y suscripción | El POST no se procesa | Worker con Turnstile y Email Routing, o un servicio externo |
| Mi cuenta | Sin backend | Eliminar |
| Búsqueda | Sin backend | Búsqueda en cliente (índice JSON) |

## 9. Migración y SEO
| ID | Requisito |
|---|---|
| RM-01 | Todas las URL indexadas hoy responden 200 con la misma ruta, o 301 a su reemplazo (`public/_redirects`) |
| RM-02 | `sitemap.xml` con el dominio final, enviado a Search Console el día del cambio |
| RM-03 | Propiedad de dominio en Search Console verificada por TXT, replicada en el DNS nuevo |
| RM-04 | El DNS nuevo replica MX, SPF y DKIM del correo actual (cPanelHost) antes de cambiar los NS en NIC Chile |
| RM-05 | Línea base de Search Console (clics, impresiones, consultas y páginas principales) exportada antes del cambio; comparación semanal durante 8 semanas |
| RM-06 | Medición de conversiones de Google Ads con Consent Mode v2; la CSP se amplía solo con los dominios de Google estrictamente necesarios |

## 10. Trabajo futuro
- Trusted Types en modo Report-Only con endpoint `report-to`.
- Reemplazar el carrito por un flujo de pedido por WhatsApp y retirar WooCommerce JS.
- Retirar páginas de demo en inglés (`/about/`, `/services/`, `/reviews/`, `/why-choose-us/`, `/sample-page/`, `/hello-world/`, producto `wea`) si el negocio lo aprueba.
- Generar `sitemap.xml` con el dominio definitivo.
