# Política de seguridad

## Reportar una vulnerabilidad
Usa **GitHub → Security → Report a vulnerability** (reporte privado) o escribe a contacto@corvimet.cl. No abras issues públicos para vulnerabilidades.

Respuesta inicial en un plazo de 5 días hábiles.

## Alcance
- El sitio publicado desde `public/` y su configuración (`config/_headers`, `wrangler.jsonc`)
- Scripts de `tools/` y workflows de `.github/`

El WordPress original en corvimet.cl está **fuera de alcance**: este repositorio solo contiene la copia estática.

## Medidas aplicadas
Ver [docs/SSD.md §6](docs/SSD.md): CSP estricta, HSTS con preload, COOP/CORP, Permissions-Policy, ningún recurso de terceros, security.txt (RFC 9116), CI con permisos mínimos y Actions fijadas por SHA.
