# Documentación del sitio corvimet.cl

Relevamiento del sitio en producción (fecha: 2026-11-18), previo a la copia.

## 1. Resumen

| Aspecto | Valor |
|---|---|
| URL | https://corvimet.cl/ |
| Rubro | Venta de maquinaria para construcción (betoneras, hormigoneras, placas compactadoras, moldes) |
| CMS | WordPress 7.1.4 |
| E-commerce | WooCommerce 5.4.4 |
| Tema | Astra 2.6.2 |
| Constructor visual | Elementor + Elementor Pro + Ultimate Addons for Elementor (`ultimate-elementor`) |
| Servidor | Apache con caché LiteSpeed (`X-LiteSpeed-Tag`) |
| Idioma | `es-CL` (algunas páginas de la plantilla quedaron en inglés: About, Services, Reviews…) |
| robots.txt | Bloquea solo `/wp-admin/`; sitemap en `/wp-sitemap.xml` |

## 2. Plugins detectados

| Plugin | Uso en el sitio |
|---|---|
| `elementor`, `elementor-pro` | Maquetación de todas las páginas, header y footer (plantillas de Theme Builder) |
| `ultimate-elementor` | Widgets adicionales de Elementor |
| `woocommerce` | Catálogo, fichas de producto, carrito, checkout, mi cuenta |
| `wpforms-lite` | Formularios (contacto/suscripción) |
| `cookie-law-info` | Banner de cookies ("Privacy Overview") |
| `click-to-chat-for-whatsapp` | Botón flotante de WhatsApp |

## 3. Mapa del sitio

### Navegación principal
`Inicio` (/) · `Categorías` (/#categorias) · `Tienda` (/store) · `Nosotros` (/#nosotros) · `Contacto` (/#contacto)

Categorías, Nosotros y Contacto son **anclas dentro de la portada**, no páginas aparte.

### Páginas (`wp-sitemap-posts-page-1.xml`)
| URL | Título | Nota |
|---|---|---|
| `/` | Corvimet | Portada (Elementor id 630) |
| `/store/` | Store | Tienda que se enlaza en el menú |
| `/tienda/` | Products | Página de tienda de WooCommerce |
| `/carrito/` | Carrito | Dinámica (WooCommerce) |
| `/finalizar-compra/` | — | Redirige (302) al carrito cuando está vacío |
| `/mi-cuenta/` | Mi cuenta | Login de cliente (dinámica) |
| `/about/`, `/services/`, `/contact/`, `/why-choose-us/`, `/reviews/` | (en inglés) | Restos de la plantilla de demostración, fuera del menú |
| `/sample-page/`, `/hello-world/` | | Contenido por defecto de WordPress |

### Productos (`/producto/...`) — 18
betonera-130l-xl-electrica, betonera-150l-bencinera, betonera-150l-electrica, cercha-vibradora,
hormigonera-150l-bencinera, hormigonera-150l-electrica, hormigonera-200l-bencinera,
hormigonera-200l-electrica, hormigonera-400l-bencinera, hormigonera-400l-electrica,
mesa-vibradora, molde-placa, molde-poste, placa-compactadora, trompo-eco-150l,
unidad-motriz-bencinera, unidad-motriz-electrica, `wea` (producto de prueba).

### Categorías de producto (`/categoria-producto/...`)
`betoneras`, `placas`, `hormigon`

### Otros
- Categoría de blog: `/category/uncategorized/`
- Autor: `/author/admin/`
- 18 plantillas de Elementor (`/?elementor_library=...`): top1, top2, topfoot, foot1, foot-final, ban1, ban2, categorias-final, nosotros-final, productos-final, contacto-final, tienda-1-final, tienda-2-final, gracias, sus, politicas, default-kit, default-kit-2.

## 4. Portada: secciones

1. Header (logo + menú)
2. **Nuestras categorías** (`#categorias`)
3. **Productos destacados**: Molde poste, Molde placa, Mesa vibradora, Hormigonera 200L bencinera
4. **Nosotros** (`#nosotros`)
5. **Contacto** (`#contacto`): teléfonos, correo y mapa de Google Maps embebido (Maipú)
6. Popups de Elementor: "Gracias por contactarnos…", "Política de entrega", "Suscríbete y recibe grandes beneficios"
7. Footer + banner de cookies + botón de WhatsApp

## 5. Datos de contacto publicados

- Correo: contacto@corvimet.cl
- Teléfonos: +56 9 3775 8648 · +56 9 8524 0116 · +56 9 4105 8461
- Ubicación del mapa: Maipú (iframe `maps.google.com`)

## 6. Diseño

- Tipografías (Google Fonts): **Montserrat** 500 (texto), **Quicksand** 500 (títulos); Elementor además carga Roboto, Roboto Slab, Poppins, Bayon y Oswald.
- Color de enlaces: `#19647e`; hover `#000000`.
- Logo: 244 px de ancho máximo.
- Portada: unos 161 KB de HTML, 32 scripts, 25 hojas de estilo y 12 imágenes.

## 7. Recursos externos

| Host | Uso |
|---|---|
| fonts.googleapis.com / fonts.gstatic.com | Fuentes |
| maps.google.com | Mapa embebido (iframe; se mantiene en línea) |
| s.w.org | Emojis de WordPress |

## 8. Tienda y pagos (observado el 2026-11-18)

- **Pasarela:** Flow (plugin `flowpaymentfl`, método `flow_flow`), con el texto "Paga con tarjetas de débito o crédito". Es el único medio de pago.
- **Despacho:** no configurado; el total es igual al subtotal.
- **Campos del checkout:** nombre, apellido, empresa, país, dirección (2 líneas), ciudad, región, código postal, teléfono y correo. **No pide RUT.**
- **Catálogo:** 18 productos simples sin variaciones; precios en CLP de $333.200 a $1.963.500. Categorías: Betoneras (11), Hormigón (6) y Placas (1).
- **Medición:** sin Google Analytics, Ads ni Tag Manager.

## 9. Infraestructura (DNS consultado el 2026-11-18)

Hosting y correo en cPanelHost (A `190.107.177.34`, MX `mail.corvimet.cl`, NS `ns1/ns2.cpanelhost.cl`). Detalle en [03-google-correo-migracion.md](03-google-correo-migracion.md).

## 10. Partes dinámicas (no funcionan en una copia estática)

Dependen de PHP y de la base de datos de WordPress:

- Carrito, checkout, "Mi cuenta" y "Añadir al carrito" (`wc-ajax`, `admin-ajax.php`)
- Envío de formularios WPForms y de suscripción
- Búsqueda (`?s=`)
- Fragmentos del carrito de WooCommerce (`wc-cart-fragments`)

Para estas partes la copia muestra la interfaz, pero la acción no se completa. Se reemplazan en las etapas 2 (formulario), 4 (mantenedor) y 5 (tienda con Flow); ver [04-producto-y-mejoras.md](04-producto-y-mejoras.md).
