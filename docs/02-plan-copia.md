# Plan de copia de corvimet.cl

## Objetivo
Obtener una copia local **completa y navegable** del sitio (todas las páginas, productos, categorías y plantillas, con su HTML, CSS, JS, imágenes y fuentes) en `site/`, que se vea igual que el original sin depender de corvimet.cl.

## Enfoque
WordPress genera HTML en el servidor, así que la forma fiel de copiarlo es un **mirror estático**. El sitio no es una SPA, por lo que no hace falta reconstruir código fuente. REA (instalado como MCP) se usa como **verificación**: captura y compara en el navegador el original y la copia, y detecta recursos que se cargan por JavaScript.

## Pasos

1. **Descubrimiento**: semillas = portada + todos los sitemaps (páginas, 18 productos, 3 categorías, plantillas de Elementor, autor, blog).
2. **Crawl de páginas** con [tools/mirror.py](../tools/mirror.py):
   - Solo el dominio `corvimet.cl`, respetando robots.txt (sin `/wp-admin/`)
   - Excluye feeds, `wp-json`, `wp-login`, `?add-to-cart`, búsquedas
   - Pausa de 150 ms entre peticiones
3. **Descarga de recursos**: `link`, `script`, `img`, `srcset`/`data-srcset`, `style="background:url()"`, `url()` y `@import` dentro del CSS, URLs escapadas en JSON de Elementor (`https:\/\/corvimet.cl\/...`), Google Fonts (CSS + woff2) en `site/_ext/<host>/`.
4. **Reescritura de URLs**: absolutas `https://corvimet.cl/...` a rutas relativas a la raíz (`/...`); recursos externos a `/_ext/...`. Las queries `?ver=` se ignoran (no cambian el contenido).
5. **Manifiesto**: `site/_mirror_manifest.json` con cada URL a su archivo local, más la lista de fallos.
6. **Verificación**:
   - Servir con `python tools/serve.py 8765` (aplica `_headers`)
   - Buscar referencias rotas (archivos referenciados que no existen) y restos de `corvimet.cl`
   - Usar REA/navegador para capturar la portada y una ficha de producto en el original y en la copia, comparar capturas de pantalla y revisar peticiones 404 (chunks de Elementor cargados de forma diferida)
7. **Iteración**: descargar los recursos faltantes que aparezcan en el paso 6 y volver a ejecutar la reescritura.

8. **Endurecimiento** ([tools/harden.py](../tools/harden.py)): `site/` → `public/`. Extrae el JS y el CSS en línea, quita huellas de WordPress, auto-aloja recursos de terceros y aplica cabeceras de `config/_headers`. Diseño en [SSD.md](SSD.md).
9. **Publicación**: GitHub (CI de verificación) → Cloudflare Workers Builds (`wrangler.jsonc`).

## Estado de ejecución (2026-11-18)
| Paso | Estado |
|---|---|
| 1 a 5. Mirror | Hecho: 86 URLs, 37 páginas únicas, 3 fallos que también fallan en el origen |
| 6 y 7. Verificación e iteración | Hecho: `verify.py` 0 errores; Chrome Canary 0 violaciones de CSP y 0 errores JS |
| 8. Endurecimiento | Hecho |
| 9. Publicación | Pendiente: crear el repo en GitHub y conectar Cloudflare |

## Estructura del proyecto

```
Corvimet.cl/
├── docs/        SSD, documentación y plan
├── config/      _headers, robots.txt, security.txt
├── tools/       mirror · harden · verify · serve · check-browser
├── site/        mirror en bruto (gitignored)
└── public/      sitio publicado
```

## Limitaciones conocidas
- Carrito, checkout, mi cuenta, formularios y búsqueda no funcionan sin WordPress (ver documentación, sección 8).
- El mapa de Google sigue en línea (iframe).
- `/finalizar-compra/` se guarda como el carrito vacío (el servidor redirige).

## Siguientes pasos (fuera de este alcance)
Decidir si la copia será un sitio estático (y reemplazar carrito y formularios por WhatsApp o un servicio externo) o una migración real de WordPress (exportar la base de datos y `wp-content`, lo que requiere acceso al hosting).
