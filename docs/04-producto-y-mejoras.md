# Producto y mejoras: la idea del sitio de Corvimet

Qué queremos lograr con el sitio, para quién y cada mejora con su motivo y su criterio de aceptación. El diseño técnico está en el [SSD](SSD.md); este documento explica el **qué** y el **porqué**.

---

## 1. Visión

> **corvimet.cl tiene que vender y cotizar solo, desde el celular, y Corvimet tiene que poder mantenerlo sin depender de nadie.**

Corvimet fabrica maquinaria para construcción (betoneras, hormigoneras, placas compactadoras, mesas vibradoras, cerchas vibradoras, moldes y unidades motrices) y la vende en Chile. Hoy el sitio muestra los productos, pero no ayuda a decidir la compra:
- Las fichas no tienen descripción ni datos técnicos.
- En el celular, los avisos tapan la pantalla.
- Cambiar un precio exige entrar a WordPress.
- No se mide qué funciona.

El sitio nuevo se apoya en tres pilares:

| Pilar | Qué significa | Cómo se mide |
|---|---|---|
| **Vender** | Comprar con Flow o cotizar por WhatsApp en menos de un minuto desde el celular | Compras y clics a WhatsApp (conversiones en GA4 y Ads) |
| **Informar** | Cada producto responde las preguntas del comprador: capacidad, motor, potencia, peso, medidas, garantía, plazo y despacho | Menos consultas repetidas; más tiempo en la ficha |
| **Autonomía** | Corvimet cambia precios, programa ofertas y actualiza productos en minutos | Cambios hechos sin pedírselos al desarrollador |

Además: **seguridad** sin WordPress expuesto, **velocidad** con Core Web Vitals en verde y **posicionamiento** que se mantiene y crece.

## 2. A quién le habla el sitio

| Perfil | Qué busca | Qué necesita ver |
|---|---|---|
| **Contratista o constructora** | Equipos confiables para obra; compra por volumen o repetida | Ficha técnica completa, ficha descargable para su área de compras, despacho y factura |
| **Maestro o particular** | Una betonera para su obra o para arrendarla | Precio claro, eléctrica o bencinera, capacidad, fotos reales y WhatsApp para preguntar |
| **Fabricante de prefabricados** | Moldes de poste o placa y mesas vibradoras | Medidas del molde, producción por jornada y garantía |
| **Cliente que vuelve** | Repuestos o un segundo equipo | Encontrar el modelo rápido (buscador, categorías) |

La mayoría llega **desde Google y desde el celular**, muchas veces desde la obra. Por eso el diseño se piensa primero para el celular, con botones grandes y carga rápida con datos móviles.

## 3. Principios de diseño
1. **El producto primero:** foto, precio y botón de compra visibles sin hacer scroll en el celular.
2. **Nada tapa la pantalla al entrar:** sin popups bloqueantes; el aviso de cookies es una franja pequeña.
3. **Una acción principal por pantalla:** "Comprar", con "Cotizar por WhatsApp" como alternativa.
4. **Identidad Corvimet:** amarillo y negro del logo, tipografía robusta y fotos reales de los equipos y de obras.
5. **Claridad antes que adornos:** español correcto, con tildes, sin texto de relleno ni plantillas en inglés.
6. **Rápido por diseño:** imágenes AVIF o WebP, una o dos tipografías (hoy se cargan siete) y JS mínimo.
7. **Accesible:** contraste AA, textos alternativos en las fotos y navegable con teclado.

## 4. Mapa del sitio objetivo

```
corvimet.cl
├── /                         Portada: propuesta de valor, categorías, destacados, confianza, contacto
├── /tienda/                  Catálogo con filtros (categoría, motor eléctrico o bencinero, capacidad)
├── /categoria-producto/…     Betoneras · Hormigón · Placas (mismas URL de hoy)
├── /producto/…               18 fichas (mismas URL de hoy; /producto/wea/ pasa a un slug correcto con 301)
├── /carrito/                 Carrito
├── /pedido/resultado         Resultado del pago Flow
├── /politica-de-entrega/     Página fija (reemplaza el popup)
├── /contacto/                Formulario, WhatsApp, teléfonos, mapa con la dirección real y horario
└── /admin/                   Mantenedor (privado)

Se eliminan con 301: /about/ /services/ /reviews/ /why-choose-us/ /sample-page/ /hello-world/ /store/ (duplicado de /tienda/), /author/admin/
```

## 5. Mejoras por etapa

Cada etapa se entrega en el entorno de **preview** y el cliente la aprueba antes de pasar a producción ([05](05-despliegue-y-entornos.md)).

### Etapa 1: Correcciones
| Mejora | Motivo (hallazgo del diagnóstico) | Criterio de aceptación |
|---|---|---|
| Traducir "Add to cart", "Related products", "Category" y el detalle de cookies | Textos de plantilla en inglés se ven descuidados | 0 textos en inglés visibles |
| Eliminar las páginas de demo y el producto `wea` (con 301) | Google las indexa y pueden aparecer en lugar de las reales | Las URL responden 301; ninguna página de demo en el sitemap |
| Unificar el correo (`contacto@` o `info@`) | Hoy el popup dice `info@` y el resto `contacto@` | Un solo correo en todo el sitio |
| Política de entrega como página fija, sin el Covid-19 | El popup tapa toda la pantalla del celular y está desactualizado | No hay popup bloqueante; la página existe y se enlaza desde el pie y el checkout |
| Banner de cookies compacto que no choque con WhatsApp | Hoy ocupa media pantalla y WhatsApp tapa "Ajustes de Cookies" | Banner de 20 % o menos del alto; ningún botón tapado |
| Tildes: "Categorías", "Hormigón", "Política" | Presentación | Revisión ortográfica completa |
| Mapa con la dirección real | Hoy busca "Maipú" en general | El mapa muestra la dirección de Corvimet |

### Etapa 2: Fichas y cotización
| Mejora | Motivo | Criterio de aceptación |
|---|---|---|
| **Ficha técnica estructurada** por producto (§6) | Los 18 productos no tienen descripción ni datos técnicos | 18 de 18 fichas completas y aprobadas por el cliente |
| Descripción y usos recomendados | Ayuda a elegir y mejora el SEO | Texto propio por producto, sin copiar entre fichas |
| Dos o más fotos por producto, optimizadas | 277 imágenes pesan 22 MB en JPG y PNG | AVIF o WebP con `srcset`; peso de la ficha de 1 MB o menos |
| **"Cotizar por WhatsApp"** con mensaje prellenado | Muchos compradores quieren conversar antes | El clic abre WhatsApp con producto, precio y cantidad |
| Formulario de contacto real con Turnstile | Hoy no se procesa ni filtra spam | El mensaje llega al correo y el remitente recibe confirmación |
| SEO on-page: título y descripción por página, `Product` JSON-LD, sitemap | Más visibilidad en Google | Resultado válido en la prueba de resultados enriquecidos |

### Etapa 3: Diseño nuevo
| Mejora | Motivo | Criterio de aceptación |
|---|---|---|
| Portada nueva: qué hace Corvimet, 3 categorías con foto, destacados con precio y prueba social | Hoy la portada no dice claramente qué vende ni por qué elegirlos | Cliente aprueba el diseño en el celular y en el escritorio |
| Tienda con filtros (categoría, motor y capacidad) | Hay 11 betoneras u hormigoneras parecidas | Filtrar a un modelo en 2 toques o menos |
| Sección de confianza: fabricación propia, garantía, despacho, obras y clientes | Genera confianza para una compra de alto valor | Sección publicada con contenido real |
| Buscador ("400L", "bencinera") | Encontrar rápido el modelo | Resultados al escribir, sin servidor de búsqueda |
| Menos JS y tipografías | Hoy hay 7 tipografías y unos 47 scripts por página | Core Web Vitals en verde en el celular |

### Etapa 4: Mantenedor de productos
Pantallas del mantenedor (`/admin`):

| Pantalla | Qué permite | Criterio de aceptación |
|---|---|---|
| **Productos** (lista) | Ver todos con su precio vigente, si hay oferta activa y si está visible o agotado; buscar y ordenar | Carga en menos de 1 s; usable en el celular |
| **Editar producto** | Nombre, descripción, ficha técnica, fotos (subir, ordenar, principal), categoría, visible, agotado y slug (crea un 301) | Los cambios se ven en el sitio al guardar |
| **Precio y oferta** | Precio normal; oferta con precio, inicio y término (hora de Chile); vista previa | La oferta empieza y termina sola; el sitio muestra el precio normal tachado |
| **Pedidos** | Lista con filtros por estado; detalle con datos de despacho; cambiar a despachado o entregado | Cada pedido pagado aparece sin intervención |
| **Historial** | Quién cambió qué y cuándo | Todo cambio de precio queda registrado |
| **Configuración** | Despacho (modo, zonas y tarifas), correo de avisos | Editable sin el desarrollador |

Acceso: cada administrador entra con **su correo y un código de un solo uso**, sin contraseñas. El acceso se quita desde Cloudflare Access.

### Etapa 5: Tienda con Flow
| Mejora | Motivo | Criterio de aceptación |
|---|---|---|
| Carrito y checkout simples (una página) | El checkout de WooCommerce es largo y en partes está en inglés | Compra completada en 5 campos más el pago |
| Pago con **Flow** (tarjetas de débito y crédito) | Es la pasarela que Corvimet ya usa | Compra real de bajo monto pagada de punta a punta |
| RUT en el checkout | Necesario para boleta o factura; hoy no se pide | Validación del dígito verificador |
| Avisos: correo al comprador y aviso a Corvimet | Que ningún pedido pase inadvertido | Ambos correos llegan al confirmarse el pago |
| Despacho configurable | Hoy no se cobra ni se informa | Funciona el modo elegido por el cliente |
| Página de resultado clara | Que el comprador sepa qué pasó | Mensajes de pagado, pendiente y rechazado con siguiente paso |

### Publicación
Google (Search Console, GA4, conversiones de Ads con Consent Mode v2, Business), traslado del dominio y del correo, y seguimiento de 8 semanas. Detalle en [03](03-google-correo-migracion.md).

## 6. Plantilla de ficha técnica

Cada producto se completa con este modelo (lo llena Corvimet; el mantenedor lo guarda como pares clave y valor):

| Campo | Ejemplo (betonera) | Aplica a |
|---|---|---|
| Capacidad del tambor | 150 L | Betoneras y hormigoneras |
| Capacidad de mezcla útil | — | Betoneras y hormigoneras |
| Motor | Eléctrico monofásico / Bencinero 4T | Todos los motorizados |
| Potencia | — HP / — kW | Motorizados |
| Voltaje | 220 V | Eléctricos |
| Peso | — kg | Todos |
| Medidas (largo × ancho × alto) | — cm | Todos |
| Ruedas o transporte | — | Betoneras y placas |
| Fuerza de compactación | — kN | Placa compactadora |
| Medidas del molde y piezas por jornada | — | Moldes y mesas vibradoras |
| Garantía | — meses | Todos |
| Plazo de entrega | 5 a 7 días hábiles (fabricación a pedido) | Todos |
| Usos recomendados | Texto | Todos |

## 7. Indicadores de éxito
| Indicador | Fuente | Meta inicial (a revisar con la línea base) |
|---|---|---|
| Compras online por mes | D1 y GA4 | Crecer respecto del WooCommerce actual |
| Clics a WhatsApp y llamadas | GA4 y Ads | Medidos desde el día 1 (hoy no se miden) |
| Clics e impresiones orgánicas | Search Console | Sin caída a las 8 semanas; crecimiento después |
| Core Web Vitals (móvil) | CrUX y PageSpeed | Los tres en verde |
| Costo por conversión de Ads | Google Ads | Medible y en baja (hoy no se mide) |
| Tiempo para cambiar un precio | Mantenedor | Menos de 1 minuto, sin el desarrollador |
| Cabeceras de seguridad | securityheaders.com | A+ |

## 8. Lo que se necesita del cliente
Lista viva para cada etapa:
- **Etapa 1:** correo oficial, número de WhatsApp para las cotizaciones, texto de la política de entrega, dirección y horario.
- **Etapa 2:** fichas técnicas (§6) y fotos.
- **Etapa 4:** correos de los administradores.
- **Etapa 5:** acceso a Flow (claves ingresadas por el titular), reglas de despacho y forma de emitir la boleta o factura.
- **Publicación:** accesos de Google, NIC Chile y cPanelHost, uso del correo @corvimet.cl, y titular de la cuenta de Cloudflare.
