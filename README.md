# Corvimet: sitio web estático

Réplica estática y endurecida de [corvimet.cl](https://corvimet.cl/) (maquinaria para construcción: betoneras, hormigoneras, placas compactadoras y moldes), publicada con **Cloudflare Workers Static Assets** desde este repositorio.

- 37 páginas (portada, tienda, 18 productos, 3 categorías) y todos sus recursos auto-alojados
- CSP estricta (`script-src 'self'`, sin `unsafe-inline` en scripts), HSTS con preload, COOP/CORP y Permissions-Policy
- Verificado en Chrome Canary: 0 violaciones de CSP y 0 errores JS

## Estructura
```
public/        Sitio publicado (generado; no editar a mano)
config/        _headers, robots.txt, security.txt (fuente editable)
tools/         mirror.py · harden.py · verify.py · serve.py · check-browser.mjs
docs/          SSD.md, documentación del sitio original y plan
wrangler.jsonc Configuración de Cloudflare
```

## Uso
```bash
pip install -r requirements.txt

python tools/mirror.py      # 1. descarga corvimet.cl a site/ (solo si cambia el original)
python tools/harden.py      # 2. genera public/ endurecido
python tools/verify.py      # 3. verificación estática
python tools/serve.py 8765  # 4. servidor local con las cabeceras reales
node tools/check-browser.mjs http://127.0.0.1:8765 / /store/ /producto/molde-poste/
```
`check-browser.mjs` usa Chrome Canary por defecto. Para usar otro navegador, define `CHROME_PATH`.

## Despliegue
1. Cloudflare Dashboard → Workers & Pages → Create → Import a repository → este repo.
2. Build command: *(vacío)*. Deploy command: `npx wrangler deploy`.
3. Cada push a `main` despliega. GitHub Actions ejecuta antes las verificaciones.
4. Dominio propio: Settings → Domains & Routes. Ajustes de TLS recomendados en [docs/SSD.md §6](docs/SSD.md).

## Limitaciones
Carrito, checkout, cuentas, formularios y búsqueda requerían WordPress y no funcionan en la versión estática. Ver [docs/SSD.md §8](docs/SSD.md).

## Documentación
- [docs/SSD.md](docs/SSD.md): especificación y diseño
- [docs/01-documentacion-sitio.md](docs/01-documentacion-sitio.md): relevamiento del sitio original
- [docs/02-plan-copia.md](docs/02-plan-copia.md): plan de ejecución
- [SECURITY.md](SECURITY.md): reporte de vulnerabilidades

El contenido, la marca y las imágenes pertenecen a Corvimet. Publica este repositorio solo con su autorización.
