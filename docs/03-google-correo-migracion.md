# Google, correo y migración del dominio

Procedimientos para instalar las herramientas de Google, trasladar el correo y cambiar corvimet.cl al servidor nuevo sin perder posicionamiento. La instalación de Google es parte del alcance ofrecido (ver [SSD §9](SSD.md)).

## 1. Estado actual (DNS consultado el 2026-11-18)

| Registro | Valor |
|---|---|
| NS | `ns1.cpanelhost.cl`, `ns2.cpanelhost.cl` |
| A | `190.107.177.34` (cPanelHost) |
| MX | `mail.corvimet.cl` (mismo servidor: el correo vive en cPanelHost) |
| TXT (SPF) | `v=spf1 +a +mx +ip4:190.107.177.34 +ip4:200.63.100.99 include:_spf.cpanelhost.cl ~all` |
| Google | Sin `google-site-verification` en DNS ni en HTML; sin gtag, GTM ni Analytics en el sitio |

Antes de tocar nada, exportar la zona DNS completa desde cPanel (Zone Editor). Incluye DKIM (`default._domainkey`), `autodiscover`, `webmail` y otros registros que no se ven desde fuera.

## 2. Herramientas de Google (incluidas en el alcance)

Propiedad de las cuentas: **Corvimet** (cuenta Google del negocio) como propietario; el desarrollador, como administrador. Nunca al revés.

| Herramienta | Configuración |
|---|---|
| Search Console | Propiedad de **dominio** `corvimet.cl`, verificada con un registro TXT. Copiar ese TXT al DNS nuevo **antes** del cambio de NS. Enviar `/sitemap.xml` el día del cambio |
| Google Analytics 4 | Propiedad nueva o existente; flujo web `https://corvimet.cl`; vincular con Search Console y con Google Ads |
| Google Ads | Conversiones: clic en `wa.me`/`api.whatsapp.com`, clic en `tel:`, envío de formulario. Importar los eventos de GA4 o usar la etiqueta de conversión de Ads |
| Google Business Profile | Dirección, horario, categorías, fotos y enlace a corvimet.cl |
| Consent Mode v2 | Valores por defecto `denied` para `ad_storage`, `ad_user_data`, `ad_personalization` y `analytics_storage`; se actualizan desde el banner de cookies |

### 2.1 Implementación sin romper la CSP
- **Sin scripts en línea:** la configuración de `gtag()` (consent default + config) va en un archivo propio `/assets/js/gtag-init.js`, cargado antes de `https://www.googletagmanager.com/gtag/js?id=…`. Así la CSP sigue sin `'unsafe-inline'` ni nonces, que requieren servidor dinámico.
- El banner de cookies actual (`cookie-law-info`) se reemplaza o adapta para llamar a `gtag('consent','update',…)`.
- Eventos de conversión: escuchar clics sobre `a[href^="https://wa.me"]`, `a[href^="tel:"]` y el envío del formulario, también desde el archivo externo.

### 2.2 Cambios en la CSP (`config/_headers`)
Hosts de la guía oficial de Google, [CSP para la etiqueta de Google](https://developers.google.com/tag-platform/security/guides/csp), secciones "Google Analytics" (con funciones de Ads) y "Google Ads". Google exige escribir cada dominio de país por separado; para Chile, `google.cl`.

| Directiva | Se agrega |
|---|---|
| `script-src` | `https://www.googletagmanager.com https://www.googleadservices.com https://www.google.com` |
| `img-src` | `https://www.googletagmanager.com https://*.google-analytics.com https://*.google.com https://*.google.cl https://*.g.doubleclick.net https://www.googleadservices.com https://googleads.g.doubleclick.net https://pagead2.googlesyndication.com` |
| `connect-src` | `https://www.googletagmanager.com https://*.google-analytics.com https://*.google.com https://*.google.cl https://*.g.doubleclick.net https://pagead2.googlesyndication.com https://www.googleadservices.com https://googleads.g.doubleclick.net https://ad.doubleclick.net` |
| `frame-src` | `https://www.googletagmanager.com` (además de Maps) |

Al hacer este cambio:
- Actualizar `tools/verify.py` (lista de hosts permitidos) y SSD §4.2 y §6 (RS-03 deja de ser "ningún tercero"; pasa a "solo Google, para medición").
- Revisar `Permissions-Policy`: no bloquear `attribution-reporting` si Ads lo usa.
- Verificar con [Tag Assistant](https://tagassistant.google.com) y `tools/check-browser.mjs` (0 violaciones de CSP) antes de publicar.

## 3. Correo @corvimet.cl

Se puede trasladar. Opciones (precios de referencia a noviembre de 2026; confirmar antes de contratar):

| Opción | Costo | Notas |
|---|---|---|
| Solo correo en cPanelHost | Plan actual | Sin cambios para los usuarios; se mantiene ese contrato |
| [Google Workspace](https://support.google.com/a/answer/15400543) Business Starter | USD 7 por usuario al mes (anual) o USD 8,40 (flexible), más IVA | Gmail, migración de datos por IMAP desde cPanel |
| [Zoho Mail](https://www.zoho.com/mail/pricing) Forever Free | USD 0, hasta 5 usuarios y 5 GB cada uno | Solo web y app propia: sin IMAP, POP ni ActiveSync; disponible en algunos data centers |
| Cloudflare Email Routing | USD 0 | **Solo reenvía**: no permite enviar como @corvimet.cl sin un servicio adicional. No recomendado como correo principal |

Procedimiento:
1. Inventario de casillas (cuántas, de quién, tamaño) en cPanel.
2. Crear las mismas casillas en el proveedor elegido.
3. Migrar el contenido por IMAP cuando el proveedor lo permita.
4. Bajar el TTL de MX a 300 s un día antes; cambiar MX, SPF (`include:` del proveedor nuevo), DKIM y DMARC (`p=none` al inicio, con reportes; endurecer después).
5. Mantener cPanelHost activo como mínimo 30 días después del cambio.

## 4. Cambio del dominio sin perder posicionamiento (runbook)

| # | Paso | Detalle |
|---|---|---|
| 1 | Línea base | Exportar de Search Console 16 meses de clics, impresiones, consultas y páginas; listar las URL indexadas |
| 2 | Redirecciones | `public/_redirects` con 301 para cada URL que se elimine (plantillas en inglés, `/producto/wea/` → slug nuevo, `/author/admin/` → `/`). Toda URL indexada debe responder 200 o 301 |
| 3 | SEO técnico | `<link rel=canonical>` con el dominio final, `sitemap.xml` y `robots.txt` con la URL del sitemap, datos estructurados `Product` y `Organization` |
| 4 | DNS nuevo | Agregar corvimet.cl a Cloudflare e importar la zona exportada de cPanel (MX, SPF, DKIM, TXT de Google). Revisar registro por registro |
| 5 | Staging | Publicar en `*.workers.dev`, verificar con `tools/verify.py` y `check-browser.mjs`, y obtener la aprobación del cliente |
| 6 | Cambio de NS | En NIC Chile, cambiar los NS a los de Cloudflare (lo hace el titular o un contacto técnico autorizado) |
| 7 | Dominio en el Worker | Custom Domain `corvimet.cl` y `www` (redirección 301 de `www` al apex o al revés, uno solo) |
| 8 | Día 0 | Enviar el sitemap en Search Console, inspeccionar las URL principales y probar el correo de entrada y salida |
| 9 | Seguimiento | Comparar con la línea base cada semana durante 8 semanas; corregir los 404 que reporte Search Console |
| 10 | Baja | Dar de baja el hosting de cPanelHost solo cuando el sitio y el correo estén confirmados (30 días como mínimo) |
