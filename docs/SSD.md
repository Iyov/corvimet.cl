# SSD: Especificación y Diseño del Sistema
**Proyecto:** Sitio web y tienda online de Corvimet (corvimet.cl)
**Versión:** 2.0 · **Fecha:** 2026-11-18 · **Estado:** propuesta enviada al cliente; fase 0 (copia endurecida) terminada

> Documentos relacionados: [04-producto-y-mejoras.md](04-producto-y-mejoras.md) (visión y mejoras) · [05-despliegue-y-entornos.md](05-despliegue-y-entornos.md) (cómo se publica) · [03-google-correo-migracion.md](03-google-correo-migracion.md) (Google, correo y dominio) · [01-documentacion-sitio.md](01-documentacion-sitio.md) (sitio original) · [02-plan-copia.md](02-plan-copia.md) (fase 0)

---

## 1. Propósito y alcance

Reemplazar el sitio WordPress/WooCommerce actual de **Corvimet** (fabricante chileno de maquinaria para construcción: betoneras, hormigoneras, placas compactadoras, mesas vibradoras y moldes) por un sitio **más rápido, más seguro y que venda más**. Corvimet debe poder administrarlo sin depender de un desarrollador.

El sistema final tiene tres partes:
1. **Sitio público:** catálogo, fichas de producto completas y contacto. Mantiene las URL actuales para no perder posicionamiento.
2. **Tienda online:** carrito y pago con **Flow**, la pasarela que Corvimet ya usa. Es obligatoria.
3. **Mantenedor de productos:** panel privado para precios, **ofertas programadas**, edición de productos y pedidos.

Todo corre en **Cloudflare** y el código vive en GitHub (`Iyov/corvimet.cl`).

### 1.1 Fases y etapas

| Fase o etapa | Contenido | Estado |
|---|---|---|
| **0. Copia endurecida** | Mirror del sitio actual, extracción de JS y CSS en línea, cabeceras de seguridad, CI. Base para todo lo demás | ✅ Terminada |
| **1. Correcciones** | Textos en español, eliminar páginas de demo y el producto "wea", un solo correo, política de entrega actualizada, avisos que no tapen la pantalla | Pendiente de aprobación |
| **2. Fichas y cotización** | Descripción y ficha técnica de los 18 productos, imágenes optimizadas, "Cotizar por WhatsApp", formulario de contacto, SEO on-page | Pendiente |
| **3. Diseño nuevo** | Rediseño pensado primero para el celular con la identidad actual (amarillo y negro), sección de confianza | Pendiente |
| **4. Mantenedor** | Panel privado: precios, ofertas programadas, CRUD de productos, pedidos, auditoría | Pendiente |
| **5. Tienda con Flow** | Carrito, checkout con RUT, pago Flow, notificaciones, despacho configurable | Pendiente |
| **Publicación** | Google (Search Console, GA4, Ads, Business), traslado del dominio y del correo, seguimiento SEO de 8 semanas | Pendiente |

Detalle funcional y criterios de aceptación de cada etapa en [04-producto-y-mejoras.md](04-producto-y-mejoras.md).

### 1.2 Fuera de alcance
- Emisión automática de boleta o factura electrónica (SII). Se sigue emitiendo como hoy.
- Cuentas de cliente ("Mi cuenta") e historial de compras del comprador.
- Medios de pago distintos de Flow.
- Presupuesto de anuncios de Google Ads y comisiones de Flow (los paga Corvimet directamente).

## 2. Contexto del sistema de origen

Detalle en [01-documentacion-sitio.md](01-documentacion-sitio.md).

| Aspecto | Hoy |
|---|---|
| CMS | WordPress 7.1.4 con Astra 2.6.2, Elementor, Elementor Pro y Ultimate Addons |
| Tienda | WooCommerce **5.4.4 (2021)**; 18 productos simples; 3 categorías (Betoneras, Placas, Hormigón) |
| Pago | Flow (plugin `flowpaymentfl`, método `flow_flow`, "tarjetas de débito o crédito"); único medio de pago |
| Despacho | No configurado (total = subtotal) |
| Checkout | Sin RUT |
| Hosting | cPanelHost (`190.107.177.34`), NS `ns1/ns2.cpanelhost.cl` |
| Correo | En el mismo hosting (MX `mail.corvimet.cl`) |
| Google | Sin Analytics, Ads ni verificación de Search Console |
| Dominio | `corvimet.cl` en NIC Chile; el titular es el cliente |

## 3. Actores

| Actor | Necesidad principal | Interfaz |
|---|---|---|
| **Comprador** (constructor, contratista, particular) | Ver especificaciones, comparar modelos, comprar o cotizar rápido desde el celular | Sitio público y checkout |
| **Interesado que cotiza** | Hablar antes de comprar (despacho, volumen, dudas técnicas) | "Cotizar por WhatsApp", formulario |
| **Administrador de Corvimet** | Cambiar precios, programar ofertas, actualizar productos y ver pedidos sin ayuda técnica | Mantenedor `/admin` |
| **Desarrollador** | Mantener, desplegar y monitorear | GitHub, Cloudflare, entorno local |
| **Flow** (sistema externo) | Procesar el pago y notificar el resultado | API REST + `urlConfirmation` |
| **Google** (sistema externo) | Indexar, medir y atribuir conversiones | Search Console, GA4, Ads, Business |

## 4. Requisitos

### 4.1 Sitio público (RF)
| ID | Requisito | Etapa | Verificación |
|---|---|---|---|
| RF-01 | Toda URL pública indexada hoy existe con la misma ruta, o redirige con 301 a su reemplazo | 0 y publicación | `verify.py` + crawl de la línea base |
| RF-02 | Las páginas se ven igual que el original (fase 0) o según el diseño aprobado (etapa 3) | 0 y 3 | Capturas con `check-browser.mjs` (escritorio y `MOBILE=1`) |
| RF-03 | El JS de cliente funciona (slider, menú móvil, popups, cookies) | 0 | Chrome Canary sin errores JS |
| RF-04 | Una URL inexistente devuelve la 404 con estado 404 | 0 | `not_found_handling: 404-page` |
| RF-05 | Despliegue automático al hacer push a `main` | 0 | Cloudflare Workers Builds |
| RF-06 | La copia puede regenerarse desde cero | 0 | `mirror.py` → `harden.py` |
| RF-07 | Todo el contenido en español, con tildes y sin páginas de demo | 1 | Revisión con el cliente |
| RF-08 | Ningún aviso cubre más del 30 % de la pantalla en el celular al cargar | 1 | `MOBILE=1 check-browser.mjs` |
| RF-09 | Cada producto tiene descripción, ficha técnica estructurada, 2 o más fotos y usos recomendados | 2 | Mantenedor y revisión |
| RF-10 | Botón "Cotizar por WhatsApp" con mensaje prellenado (producto, precio vigente, cantidad) | 2 | Prueba manual |
| RF-11 | Formulario de contacto con Turnstile que entrega al correo de Corvimet y confirma al remitente | 2 | Prueba de envío |
| RF-12 | Imágenes en AVIF o WebP con `srcset`; LCP < 2,5 s en 4G | 2 y 3 | Lighthouse y CrUX |
| RF-13 | Diseño pensado primero para el celular, aprobado por el cliente | 3 | Revisión en el entorno de preview |
| RF-14 | El precio mostrado siempre es el vigente en D1, con oferta y precio normal tachado | 4 | Prueba con una oferta programada |

### 4.2 Mantenedor (RA)
| ID | Requisito |
|---|---|
| RA-01 | CRUD de productos: nombre, slug, descripción, ficha técnica (clave y valor), fotos (orden y principal), categoría, orden en la tienda, visible y agotado |
| RA-02 | Precio normal y **ofertas programadas** (`sale_price`, `sale_from`, `sale_to` en `America/Santiago`). El precio vigente se calcula al consultar; la oferta empieza y termina sola |
| RA-03 | Vista previa del cambio antes de publicarlo |
| RA-04 | Lista de pedidos con filtros y estados: `pendiente_pago` → `pagado` → `despachado` → `entregado` (y `rechazado` o `anulado`) |
| RA-05 | Bitácora de auditoría: quién, qué, cuándo, valor anterior y nuevo (append-only) |
| RA-06 | Acceso por usuario (correo + OTP o Google) vía Cloudflare Access, revocable de inmediato |
| RA-07 | Cambiar el slug crea una redirección 301 automática |
| RA-08 | Subida de fotos a R2 con validación de tipo y tamaño y generación de variantes |
| RA-09 | Configuración de despacho (modo, zonas, tarifas y monto para despacho gratis) editable |
| RA-10 | Interfaz en español usable en el celular |

### 4.3 Tienda (RT)
| ID | Requisito |
|---|---|
| RT-01 | Carrito y checkout propios; el pago se procesa con la **cuenta Flow existente** de Corvimet |
| RT-02 | El pago se confirma **solo** por la notificación servidor a servidor de Flow (`urlConfirmation`), verificada con `payment/getStatus`; nunca por la redirección del navegador |
| RT-03 | Pedido idempotente: `commerceOrder` único; las notificaciones repetidas no duplican el pedido |
| RT-04 | Precios y total recalculados en el servidor desde D1; el cliente nunca envía precios |
| RT-05 | Correo de confirmación al comprador y aviso a Corvimet (correo, y WhatsApp como enlace) al confirmarse el pago |
| RT-06 | RUT obligatorio, con validación del dígito verificador |
| RT-07 | Despacho según RA-09: a coordinar, tarifa por zona o gratis sobre un monto |
| RT-08 | Página de resultado (pagado, pendiente o rechazado) consultando el estado en el servidor |
| RT-09 | Carrito persistente en el navegador (`localStorage`) que tolera precios vencidos: el servidor recalcula y avisa si cambió algo |

### 4.4 Seguridad (RS)
| ID | Requisito |
|---|---|
| RS-01 | CSP estricta: `script-src 'self'` (más los hosts de Google de RM-06), **sin** `'unsafe-inline'` ni `'unsafe-eval'` en scripts |
| RS-02 | Ningún `<script>`, `<style>` ni handler `on*` en línea en HTML servido |
| RS-03 | Sin subrecursos de terceros, salvo Google Maps (iframe), las etiquetas de Google (RM-06) y la redirección a Flow |
| RS-04 | HSTS de 2 años con `includeSubDomains` y `preload` |
| RS-05 | COOP `same-origin`, CORP `same-origin`, `Origin-Agent-Cluster`, `frame-ancestors 'none'` |
| RS-06 | Permissions-Policy restrictiva |
| RS-07 | Sin huellas de WordPress ni página `/author/` |
| RS-08 | `/.well-known/security.txt` (RFC 9116) vigente |
| RS-09 | CI con permisos mínimos y Actions fijadas por SHA; Dependabot, secret scanning y push protection |
| RS-10 | Sin secretos en el repositorio: claves de Flow y tokens solo como secrets de Cloudflare |
| RS-11 | `/admin*` y `/api/admin*` protegidos por Cloudflare Access; el Worker además valida el JWT de Access |
| RS-12 | Rate limiting en checkout, formulario y confirmación |
| RS-13 | Datos personales mínimos (Ley 19.628 y Ley 21.719); retención definida; respaldo diario de D1 |

### 4.5 Migración, SEO y Google (RM)
| ID | Requisito |
|---|---|
| RM-01 | Todas las URL indexadas hoy responden 200 o 301 (`_redirects`, más la tabla `redirects` en D1 para los cambios de slug) |
| RM-02 | `sitemap.xml` generado desde D1 con el dominio final, enviado a Search Console el día del cambio |
| RM-03 | Propiedad de dominio en Search Console verificada por TXT, replicada en el DNS nuevo |
| RM-04 | El DNS nuevo replica MX, SPF y DKIM del correo antes de cambiar los NS en NIC Chile |
| RM-05 | Línea base de Search Console exportada antes del cambio; comparación semanal durante 8 semanas |
| RM-06 | Search Console, GA4, conversiones de Google Ads (clic en WhatsApp, `tel:`, formulario y **compra**) y Google Business, con Consent Mode v2 |
| RM-07 | El correo @corvimet.cl queda resuelto (cPanelHost, Workspace o Zoho) antes de dar de baja el hosting actual |
| RM-08 | Datos estructurados `Product` (precio, disponibilidad, oferta con `priceValidUntil`), `Organization` y `BreadcrumbList` |

### 4.6 No funcionales
- **Rendimiento:** Core Web Vitals en verde (LCP < 2,5 s, INP < 200 ms, CLS < 0,1) en el celular.
- **Disponibilidad:** la de la red de Cloudflare. Sin servidor propio que mantener.
- **Costo de infraestructura:** dentro del plan gratuito de Cloudflare con el tráfico esperado (§6.5).
- **Mantenibilidad:** TypeScript, pruebas automáticas en CI y migraciones de D1 versionadas.
- **Accesibilidad:** WCAG 2.2 AA en el sitio público y el mantenedor.

## 5. Arquitectura

### 5.1 Fase 0 (actual): copia estática endurecida
```
                 ┌─────────────┐  mirror.py   ┌────────┐  harden.py   ┌──────────┐
 corvimet.cl ───►│  crawler    │─────────────►│ site/  │─────────────►│ public/  │
 (WordPress)     └─────────────┘  (en bruto,  └────────┘  (endurecido, └────┬─────┘
                                   gitignored)              versionado)     │ git push
                       verify.py + check-browser.mjs  ◄── GitHub Actions ── GitHub
                                                         Workers Builds     ▼
                                                  Cloudflare Workers Static Assets
```

### 5.2 Arquitectura final (etapas 4 y 5)
```
                          ┌───────────────────────── Cloudflare ─────────────────────────┐
 Comprador ──HTTPS──► WAF/CDN ──► Worker "corvimet" (TypeScript)                         │
                          │        ├─ Static Assets: diseño, CSS/JS, imágenes del tema    │
                          │        ├─ HTMLRewriter: precio, oferta, stock y JSON-LD       │
                          │        │   desde D1 en /producto/* y /tienda/*                │
                          │        ├─ /api/cart/quote   recalcula el carrito              │
                          │        ├─ /api/checkout ──────────────► Flow payment/create   │
                          │        ├─ /api/flow/confirm ◄───────── Flow urlConfirmation   │
                          │        │                    ──────────► Flow payment/getStatus│
                          │        ├─ /api/contact (Turnstile) ──► correo                 │
                          │        └─ /admin, /api/admin ◄── Cloudflare Access (OTP)      │
                          │   D1 (SQLite): productos, precios, pedidos, auditoría         │
                          │   R2: fotos subidas desde el mantenedor                       │
                          │   Cron Trigger: purga la caché al empezar o terminar ofertas  │
                          └───────────────────────────────────────────────────────────────┘
 Administrador ──► /admin (Access) ──► API admin ──► D1 / R2 (con auditoría)
```

**Patrón clave:** las páginas siguen siendo **HTML estático** (diseño, SEO y velocidad), y el Worker **inyecta los datos vivos** con `HTMLRewriter`: precio, oferta, disponibilidad y JSON-LD. Así:
- Un cambio de precio en el mantenedor se ve **al instante**, sin redesplegar.
- Si D1 falla, la página se sirve igual, con el último precio publicado y el botón de cotizar.
- Las URL, el diseño y el contenido indexable no dependen de JavaScript en el cliente.

### 5.3 Componentes
| Componente | Ubicación | Responsabilidad |
|---|---|---|
| Crawler | `tools/mirror.py` | Fase 0: descarga el sitio original a `site/` |
| Endurecedor | `tools/harden.py` | Fase 0: genera `public/` (extrae JS y CSS en línea, quita WordPress) |
| Configuración pública | `config/` | `_headers`, `robots.txt`, `security.txt` |
| Worker | `src/` (etapas 4 y 5) | Rutas, HTMLRewriter, API, Flow, Access |
| Esquema de BD | `migrations/` (etapa 4) | Migraciones SQL de D1 versionadas |
| Mantenedor (UI) | `admin/` (etapa 4) | SPA liviana servida como assets bajo `/admin`, sin scripts en línea |
| Verificación | `tools/verify.py`, `tools/check-browser.mjs`, `test/` | Estática, navegador (Canary) y pruebas del Worker (Vitest con `@cloudflare/vitest-pool-workers`) |
| Despliegue | `wrangler.jsonc` | Bindings: assets, D1, R2, cron y variables |

### 5.4 Decisiones de diseño
| # | Decisión | Alternativas descartadas | Motivo |
|---|---|---|---|
| D1 | Mirror estático como base (fase 0) | Migrar WordPress | Elimina la superficie de PHP y conserva diseño y URL |
| D2 | Cloudflare Workers + Static Assets | GitHub Pages, Cloudflare Pages | GitHub Pages no permite cabeceras; Cloudflare recomienda Workers para proyectos nuevos |
| D3 | Extraer JS y CSS en línea a archivos con nombre por hash | CSP con hashes o nonces | Límite de 2.000 caracteres por línea en `_headers` y más de 600 scripts en línea |
| D4 | `style-src-attr 'unsafe-inline'` | Eliminar todos los `style=""` | Elementor genera cientos de estilos en atributos; riesgo bajo |
| D5 | Sin COEP | `require-corp` o `credentialless` | Rompería el iframe de Maps |
| D6 | Sin Trusted Types (por ahora) | `require-trusted-types-for` | jQuery y Elementor usan `innerHTML`; se reevalúa con el diseño nuevo (etapa 3) |
| D7 | Excluir `/author/` | Copiarlo | Revela el usuario del WordPress real |
| D8 | Eliminar `wc-cart-fragments`, emojis y speculation rules | Mantenerlos | AJAX sin backend o recursos de terceros |
| **D9** | **Tienda y mantenedor a medida en Cloudflare** (confirmado por el usuario el 2026-11-18) | WooCommerce completo, WooCommerce headless, Jumpseller o Shopify | Máxima seguridad, sin WordPress que mantener, sin costo de hosting, URL y diseño propios |
| D10 | HTMLRewriter sobre HTML estático | SSR completo o SPA | SEO y velocidad del estático, más datos vivos y tolerancia a fallos |
| D11 | Cloudflare Access para el mantenedor | Login propio con contraseñas | Sin contraseñas que guardar ni filtrar; OTP y revocación desde el panel; gratis hasta 50 usuarios |
| D12 | Confirmar pagos solo por `urlConfirmation` + `getStatus` | Confiar en la redirección de retorno | La redirección es manipulable por el usuario |
| D13 | Carrito en `localStorage` y precio recalculado en el servidor | Carrito en el servidor con sesión | Sin sesiones ni cookies de seguimiento; el servidor sigue siendo la fuente de verdad |
| D14 | Cuenta de Cloudflare a nombre de Corvimet, con el desarrollador como administrador (recomendado; **pendiente de confirmar**) | Cuenta del desarrollador | El negocio es dueño de su infraestructura |

## 6. Entornos y despliegue

Resumen; el paso a paso está en [05-despliegue-y-entornos.md](05-despliegue-y-entornos.md).

### 6.1 Entornos
| Entorno | Dónde | Quién lo usa | Datos | Flow |
|---|---|---|---|---|
| **Local** | PC del desarrollador: `npx wrangler dev` (Worker + D1 y R2 locales con Miniflare). En fase 0, `tools/serve.py` | Desarrollador | Semilla de prueba (`migrations/` + `seed.sql`) | Sandbox |
| **Preview** | URL `*.workers.dev` de Cloudflare, protegida con Access | Cliente (aprueba cada etapa) y desarrollador | D1 de preview (copia de prueba) | Sandbox |
| **Producción** | `https://corvimet.cl` (Custom Domain del Worker) | Público y administradores (`/admin`) | D1 de producción | Producción |

### 6.2 Flujo de publicación
```
rama feature ──PR──► GitHub Actions (verify + tests) ──merge──► main
                                                                 │ Workers Builds
                                    ┌────────────────────────────┴───────────────┐
                              preview (versión subida, URL de preview)    producción (deploy)
```
- **GitHub** es la fuente de verdad del código y del historial. No sirve el sitio.
- **Cloudflare Workers Builds** conecta el repo: cada push a `main` despliega a producción en 1 o 2 minutos, y las ramas o PR generan una versión de preview.
- **Rollback:** Cloudflare guarda las versiones desplegadas; se vuelve a la anterior desde el panel o con `wrangler rollback`.
- **Migraciones de D1:** `wrangler d1 migrations apply` en preview, y luego en producción, antes del deploy que las necesita.

### 6.3 Secretos y configuración
| Nombre | Tipo | Dónde se define |
|---|---|---|
| `FLOW_API_KEY`, `FLOW_SECRET_KEY` | Secret | `wrangler secret put` (o el panel), **ingresados por el titular de Flow**. Distintos en preview (sandbox) y producción |
| `FLOW_API_BASE` | Variable | `https://sandbox.flow.cl/api` (local y preview) o `https://www.flow.cl/api` (producción) |
| `ACCESS_TEAM_DOMAIN`, `ACCESS_AUD` | Variable | Datos de la aplicación de Access, para validar el JWT |
| `TURNSTILE_SECRET` | Secret | Panel de Turnstile |
| `NOTIFY_EMAIL` | Variable | Correo que recibe los avisos de pedido |

Nada de esto va al repo (RS-10). `.dev.vars` (local) está en `.gitignore`.

### 6.4 Cómo se abre
- **Clientes:** `https://corvimet.cl`.
- **Administradores de Corvimet:** `https://corvimet.cl/admin`, con su correo y un código de un solo uso.
- **Revisión de etapas:** el enlace de preview que entrega el desarrollador (protegido con Access).
- **Desarrollo:** local con `wrangler dev`.

### 6.5 Capacidad y costo (plan gratuito de Cloudflare; verificar límites vigentes al implementar)
| Recurso | Límite gratuito de referencia | Uso esperado de Corvimet |
|---|---|---|
| Workers | 100.000 solicitudes por día | Muy por debajo (sitio de catálogo de una pyme) |
| D1 | 5 GB de almacenamiento | Menos de 50 MB (18 productos más pedidos) |
| R2 | 10 GB de almacenamiento | Menos de 1 GB de fotos |
| Access | Hasta 50 usuarios | 2 a 5 administradores |

Si se superan los límites, el plan Workers Paid parte en unos USD 5 al mes.

## 7. Modelo de datos (D1, borrador para la etapa 4)

```sql
CREATE TABLE categories (
  id INTEGER PRIMARY KEY, slug TEXT UNIQUE NOT NULL, name TEXT NOT NULL, sort INTEGER DEFAULT 0
);
CREATE TABLE products (
  id INTEGER PRIMARY KEY, slug TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
  category_id INTEGER REFERENCES categories(id), short_desc TEXT, description_md TEXT,
  price_clp INTEGER NOT NULL CHECK (price_clp >= 0),
  sale_price_clp INTEGER CHECK (sale_price_clp >= 0), sale_from TEXT, sale_to TEXT,   -- ISO 8601 con zona
  visible INTEGER NOT NULL DEFAULT 1, sold_out INTEGER NOT NULL DEFAULT 0, sort INTEGER DEFAULT 0,
  updated_at TEXT NOT NULL, updated_by TEXT NOT NULL
);
CREATE TABLE product_specs (product_id INTEGER REFERENCES products(id), k TEXT, v TEXT, sort INTEGER, PRIMARY KEY (product_id, k));
CREATE TABLE product_images (id INTEGER PRIMARY KEY, product_id INTEGER REFERENCES products(id), r2_key TEXT NOT NULL, alt TEXT, sort INTEGER, is_main INTEGER DEFAULT 0);
CREATE TABLE orders (
  id INTEGER PRIMARY KEY, commerce_order TEXT UNIQUE NOT NULL, flow_token TEXT, flow_order INTEGER,
  status TEXT NOT NULL CHECK (status IN ('pendiente_pago','pagado','rechazado','anulado','despachado','entregado')),
  rut TEXT NOT NULL, name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT, company TEXT,
  address TEXT, commune TEXT, region TEXT, shipping_mode TEXT, shipping_clp INTEGER DEFAULT 0,
  subtotal_clp INTEGER NOT NULL, total_clp INTEGER NOT NULL, created_at TEXT NOT NULL, paid_at TEXT
);
CREATE TABLE order_items (order_id INTEGER REFERENCES orders(id), product_id INTEGER, name TEXT, unit_price_clp INTEGER, qty INTEGER CHECK (qty > 0));
CREATE TABLE audit_log (id INTEGER PRIMARY KEY, at TEXT NOT NULL, actor TEXT NOT NULL, entity TEXT, entity_id TEXT, field TEXT, old_value TEXT, new_value TEXT);
CREATE TABLE redirects (from_path TEXT PRIMARY KEY, to_path TEXT NOT NULL, created_at TEXT);
CREATE TABLE settings (k TEXT PRIMARY KEY, v TEXT);   -- despacho, correo de avisos, etc.
```

**Precio vigente:** `sale_price_clp` si `sale_from <= ahora < sale_to` (en hora de Chile); si no, `price_clp`. Se calcula en una única función compartida por las páginas, el carrito y el checkout.

**Carga inicial:** los 18 productos actuales se importan desde la copia (`site/producto/*`) con un script (título, precio, categoría, fotos); las fichas técnicas las completa el cliente (etapa 2).

## 8. Rutas e interfaces

| Ruta | Método | Descripción | Protección |
|---|---|---|---|
| `/`, `/tienda/`, `/categoria-producto/*`, `/producto/*` | GET | HTML estático más datos vivos (HTMLRewriter) | Pública, en caché |
| `/carrito/` | GET | Página del carrito (JS externo, `localStorage`) | Pública |
| `/api/cart/quote` | POST | `{items:[{slug,qty}]}` → precios vigentes, despacho y total | Pública, rate limit |
| `/api/checkout` | POST | Datos del comprador más el carrito → crea el pedido y `payment/create` → `{redirect}` | Pública, rate limit, Turnstile |
| `/api/flow/confirm` | POST | `token` desde Flow → `payment/getStatus` → actualiza el pedido | Solo Flow (se valida consultando a Flow) |
| `/pedido/resultado` | GET o POST | Retorno del comprador desde Flow; muestra el estado consultado en el servidor | Pública |
| `/api/contact` | POST | Formulario de contacto | Turnstile y rate limit |
| `/sitemap.xml` | GET | Generado desde D1 | Pública |
| `/admin/*` | GET | UI del mantenedor | Cloudflare Access |
| `/api/admin/products`, `/api/admin/products/:id` | GET, POST, PATCH | CRUD de productos y precios (con auditoría) | Access + JWT + `Origin` |
| `/api/admin/images` | POST | Subida a R2 | Access + validación |
| `/api/admin/orders`, `/api/admin/orders/:id` | GET, PATCH | Pedidos y cambio de estado | Access |
| `/api/admin/settings` | GET, PATCH | Despacho y avisos | Access |

## 9. Flujos principales

### 9.1 Compra con Flow
```
Comprador            Worker                         D1            Flow
   │ POST /api/checkout ─►│ valida RUT, Turnstile, Origin  │              │
   │                      │ recalcula precios ────────────►│              │
   │                      │ INSERT pedido (pendiente_pago) ►│              │
   │                      │ payment/create (firmado HMAC) ─────────────────►│
   │◄── {redirect: url?token} ◄────────────────────────────────── url+token │
   │ ── paga en Flow ─────────────────────────────────────────────────────►│
   │                      │◄── POST urlConfirmation (token) ────────────────│
   │                      │ payment/getStatus (firmado) ───────────────────►│
   │                      │ compara monto y moneda; UPDATE pagado ────►│     │
   │                      │ correo al comprador y aviso a Corvimet           │
   │ ◄── urlReturn: /pedido/resultado (estado leído desde D1) ──────────────│
```
- **Firma Flow:** HMAC-SHA256 de los parámetros ordenados alfabéticamente (`nombre` + `valor` concatenados) con `secretKey`, enviada como `s`. Verificar contra la documentación oficial de la API v2 de Flow al implementar.
- **Idempotencia:** `commerce_order` único; si llega una confirmación de un pedido ya `pagado`, se responde 200 sin efectos.
- **Monto:** si `getStatus` informa un monto distinto de `total_clp`, el pedido queda en revisión y no se marca como pagado.

### 9.2 Oferta programada
1. El administrador define en `/admin` el precio de oferta, la fecha de inicio y la de término, y ve la vista previa.
2. Se guarda en D1 con auditoría.
3. Desde ese momento, el HTMLRewriter muestra la oferta dentro de la ventana de fechas. Al llegar `sale_from` o `sale_to`, el Cron Trigger purga la caché de esas páginas.
4. El checkout siempre recalcula con la misma función de precio vigente (RT-04).

### 9.3 Edición de producto
1. El administrador edita los campos y fotos; cambiar el slug crea una redirección 301 automática.
2. Cada campo modificado deja una entrada en `audit_log`.
3. Se purga la caché de la ficha, de la categoría, de la tienda y del sitemap.

## 10. Diseño de seguridad

### 10.1 Cabeceras (`config/_headers`)
| Cabecera | Valor actual | Amenaza mitigada |
|---|---|---|
| Content-Security-Policy | `default-src 'none'; script-src 'self'; style-src-elem 'self'; style-src-attr 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; frame-src maps.google.com www.google.com; form-action 'self'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; upgrade-insecure-requests` | XSS, inyección, exfiltración, clickjacking |
| Strict-Transport-Security | `max-age=63072000; includeSubDomains; preload` | Downgrade y SSL stripping |
| X-Content-Type-Options | `nosniff` | MIME sniffing |
| X-Frame-Options | `DENY` | Clickjacking (navegadores antiguos) |
| Referrer-Policy | `strict-origin-when-cross-origin` | Filtración de URL |
| Permissions-Policy | todas `()` salvo `fullscreen=(self)` | Abuso de APIs |
| Cross-Origin-Opener-Policy | `same-origin` | XS-Leaks |
| Cross-Origin-Resource-Policy | `same-origin` | Inclusión desde otros orígenes |
| Origin-Agent-Cluster | `?1` | Aislamiento por origen |

**Cambios previstos:**
- **Etapa 5:** `form-action 'self' https://www.flow.cl` (Chrome aplica `form-action` a las redirecciones posteriores a un POST; en preview, `https://sandbox.flow.cl`).
- **Publicación:** se agregan los hosts oficiales de Google para GA4 y Ads ([03 §2.2](03-google-correo-migracion.md)) y, si se usa en el formulario, `https://challenges.cloudflare.com` para Turnstile.
- **Respuestas del Worker:** las cabeceras de `_headers` **no** se aplican a lo que genera el código del Worker. El Worker agrega las mismas cabeceras a sus respuestas con un middleware común.

Límites de `_headers`: 100 reglas y 2.000 caracteres por línea (`verify.py` los comprueba).

### 10.2 Mantenedor
- Cloudflare Access (Zero Trust) con política por lista de correos y OTP por correo, o Google.
- El Worker valida el JWT `Cf-Access-Jwt-Assertion` (firma, `aud` e `iss`) en cada `/api/admin/*`: defensa en profundidad si Access se configurara mal.
- CSRF: verificación de `Origin` y `SameSite=Strict`; métodos de escritura solo POST, PATCH o DELETE.
- Auditoría append-only (RA-05).

### 10.3 Tienda y datos
- Los datos de tarjeta **nunca** pasan por Corvimet; los procesa Flow.
- El precio y el total se recalculan siempre en el servidor (RT-04).
- Rate limiting (binding de Rate Limiting o reglas WAF) en checkout, contacto y confirmación.
- Datos personales: solo los necesarios para despacho y boleta (Ley 19.628 y Ley 21.719). Retención propuesta de 5 años para pedidos (respaldo tributario), configurable.
- Respaldos: D1 Time Travel y export periódico a R2.
- Fotos: tipo (JPEG, PNG o WebP) y tamaño validados; servidas desde R2 con `Content-Type` correcto y `nosniff`.

### 10.4 Panel de Cloudflare (no se versiona)
SSL "Full (strict)", TLS mínimo 1.2, TLS 1.3, Always Use HTTPS, DNSSEC, WAF Managed Rules, Bot Fight Mode y 2FA obligatorio en la cuenta.

## 11. Migración, SEO y Google
Requisitos RM-01 a RM-08 (§4.5). Procedimiento, runbook de 10 pasos y CSP de Google en [03-google-correo-migracion.md](03-google-correo-migracion.md).

## 12. Verificación y pruebas
| Nivel | Herramienta | Qué valida |
|---|---|---|
| Estática | `tools/verify.py` | Sin scripts en línea, sin terceros no permitidos, referencias locales y límites de `_headers` |
| Navegador | `tools/check-browser.mjs` (Chrome Canary, escritorio y `MOBILE=1`) | 0 violaciones de CSP, 0 errores JS, 0 respuestas 4xx inesperadas, capturas |
| Worker | Vitest + `@cloudflare/vitest-pool-workers` | Precio vigente (bordes de fecha y zona horaria), firma Flow, idempotencia, validación de RUT, validación del JWT de Access |
| Integración | Flow sandbox | Compra completa: pagada, rechazada y confirmación duplicada |
| Externa | securityheaders.com, Mozilla Observatory, Lighthouse | A+ en cabeceras; Core Web Vitals en verde |
| SEO | Search Console | Sin aumento de 404 ni caída de impresiones respecto de la línea base |

**Estado fase 0:** `verify.py` 0 errores en 37 páginas; Chrome Canary 160 con 0 violaciones de CSP y 0 errores JS; CI de GitHub en verde.

## 13. Limitaciones de la fase 0
| Función | Estado en la copia | Se resuelve en |
|---|---|---|
| Carrito y checkout | Se ve la interfaz, pero no procesa | Etapa 5 (§9.1) |
| Formularios WPForms | El POST no se procesa | Etapa 2 (`/api/contact`) |
| Mi cuenta | Sin backend | Se elimina (fuera de alcance) |
| Búsqueda | Sin backend | Etapa 3 (búsqueda en el cliente sobre un índice JSON desde D1) |

## 14. Riesgos
| Riesgo | Impacto | Mitigación |
|---|---|---|
| Caída de posicionamiento al migrar | Menos visitas | Mismas URL, 301, línea base y seguimiento de 8 semanas (RM-01 a RM-05) |
| Corte del correo al cambiar el DNS | Pérdida de mensajes | Replicar MX, SPF y DKIM antes de cambiar los NS; mantener cPanelHost 30 días (RM-04, RM-07) |
| Cambios en la API de Flow | Pagos fallidos | Pruebas en sandbox, alertas ante errores de confirmación y botón de WhatsApp como respaldo |
| Configuración incorrecta de Access | Mantenedor expuesto | Validación del JWT en el Worker (§10.2) y prueba automática de que `/api/admin` sin JWT responde 403 |
| Pérdida de datos de D1 | Pedidos o productos perdidos | Time Travel y export a R2 |
| Dependencia de una sola persona | Continuidad | Cuenta de Cloudflare a nombre de Corvimet (D14), documentación en el repo y runbooks |

## 15. Trabajo futuro
- Trusted Types (Report-Only) cuando el diseño nuevo ya no dependa de jQuery ni de Elementor.
- Emisión automática de boleta o factura electrónica (SII) integrada al pedido.
- Comparador de modelos y ficha técnica descargable en PDF generada desde D1.
- Notificación de pedidos por la API de WhatsApp Business.
