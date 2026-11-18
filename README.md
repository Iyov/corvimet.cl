# Corvimet: sitio web y tienda online

Código del nuevo sitio de [corvimet.cl](https://corvimet.cl/), fabricante chileno de maquinaria para construcción (betoneras, hormigoneras, placas compactadoras, mesas vibradoras y moldes).

**Objetivo:** un sitio que **venda y cotice solo desde el celular**, con pago **Flow**, un **mantenedor** para que Corvimet actualice precios y programe ofertas sin ayuda técnica, **sin perder el posicionamiento en Google** y con las protecciones de seguridad más estrictas. Todo corre en **Cloudflare**.

> Visión y mejoras: [docs/04-producto-y-mejoras.md](docs/04-producto-y-mejoras.md) · Diseño técnico: [docs/SSD.md](docs/SSD.md) · Cómo se publica: [docs/05-despliegue-y-entornos.md](docs/05-despliegue-y-entornos.md)

## Hoja de ruta
| Etapa | Contenido | Estado |
|---|---|---|
| 0. Copia endurecida | Mirror del sitio actual, JS y CSS fuera del HTML, CSP estricta, CI | ✅ Terminada |
| 1. Correcciones | Español, sin páginas de demo, sin popups que tapen la pantalla, un solo correo | ⏳ Esperando aprobación |
| 2. Fichas y cotización | Ficha técnica de los 18 productos, fotos optimizadas, WhatsApp, formulario, SEO | ⏳ |
| 3. Diseño nuevo | Pensado primero para el celular, identidad amarilla y negra, filtros, buscador | ⏳ |
| 4. Mantenedor | `/admin`: precios, ofertas programadas, productos, pedidos, auditoría | ⏳ |
| 5. Tienda con Flow | Carrito, checkout con RUT, pago Flow, avisos y despacho | ⏳ |
| Publicación | Google (Search Console, GA4, Ads, Business), dominio, correo y seguimiento SEO | ⏳ |

## Arquitectura
```
PC (desarrollo) ──push──► GitHub ──Workers Builds──► Cloudflare ◄── corvimet.cl (NIC Chile)
                                                     Worker + Static Assets (páginas)
                                                     D1 (productos, precios, pedidos) · R2 (fotos)
                                                     Access (mantenedor) · Flow API (pagos)
```
- **Hoy (fase 0):** sitio estático endurecido en `public/`, servido por Workers Static Assets.
- **Final:** el mismo HTML más un Worker que inyecta precio, oferta y stock desde D1, procesa los pagos con Flow y expone el mantenedor protegido con Access ([SSD §5](docs/SSD.md)).

## Cómo se abre
| Quién | Dónde |
|---|---|
| Clientes | `https://corvimet.cl` (tras la publicación) |
| Administradores de Corvimet | `https://corvimet.cl/admin` (correo + código) |
| Revisión de cada etapa | Enlace de preview `*.workers.dev` (protegido) |
| Desarrollo | Local: `python tools/serve.py 8765` (fase 0) · `npx wrangler dev` (etapa 4 en adelante) |

## Estructura
```
public/        Sitio publicado (generado por tools/harden.py; no editar a mano)
config/        _headers, robots.txt, security.txt (fuente editable)
tools/         mirror.py · harden.py · verify.py · serve.py · check-browser.mjs
docs/          SSD, visión y mejoras, despliegue, Google, correo y migración, sitio original
wrangler.jsonc Configuración de Cloudflare
src/ migrations/ admin/ test/   (etapas 4 y 5: Worker, esquema D1, mantenedor y pruebas)
```

## Desarrollo local (fase 0)
```bash
pip install -r requirements.txt
python tools/mirror.py      # 1. descarga corvimet.cl a site/ (solo si cambia el original)
python tools/harden.py      # 2. genera public/ endurecido
python tools/verify.py      # 3. verificación estática
python tools/serve.py 8765  # 4. servidor local con las cabeceras reales → http://127.0.0.1:8765
node tools/check-browser.mjs http://127.0.0.1:8765 / /tienda/ /producto/molde-poste/
MOBILE=1 node tools/check-browser.mjs http://127.0.0.1:8765 /
```
`check-browser.mjs` usa **Chrome Canary** por defecto (`CHROME_PATH` para cambiarlo).

## Seguridad
CSP estricta (`script-src 'self'`, sin scripts en línea), HSTS con preload, COOP y CORP, Permissions-Policy y `security.txt`. CI con permisos mínimos y Actions fijadas por SHA; Dependabot, secret scanning y push protection. Las claves de Flow y los datos de pedidos **nunca** van al repositorio. Ver [SSD §10](docs/SSD.md) y [SECURITY.md](SECURITY.md).

## Documentación
| Documento | Contenido |
|---|---|
| [docs/04-producto-y-mejoras.md](docs/04-producto-y-mejoras.md) | Visión, público, principios de diseño, mejoras por etapa con criterios de aceptación, ficha técnica, indicadores |
| [docs/SSD.md](docs/SSD.md) | Requisitos, arquitectura, decisiones, entornos, modelo de datos, rutas, flujos (compra Flow, ofertas), seguridad, pruebas y riesgos |
| [docs/05-despliegue-y-entornos.md](docs/05-despliegue-y-entornos.md) | Cloudflare, Workers Builds, D1, R2, secretos, Access, flujo diario, paso a producción y operación |
| [docs/03-google-correo-migracion.md](docs/03-google-correo-migracion.md) | Search Console, GA4, Ads, CSP de Google, opciones de correo y runbook del cambio de dominio |
| [docs/01-documentacion-sitio.md](docs/01-documentacion-sitio.md) | Relevamiento del sitio WordPress original |
| [docs/02-plan-copia.md](docs/02-plan-copia.md) | Plan y estado de la fase 0 (copia endurecida) |
| [MEMORY.md](MEMORY.md) | Decisiones, estado y aprendizajes |
| [AGENTS.md](AGENTS.md) | Reglas para agentes de código |

---
El contenido, la marca y las imágenes pertenecen a Corvimet; se publican con su autorización. Autor del código: Francisco Barrientos.
