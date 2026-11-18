# Despliegue y entornos

Cómo pasa el sitio del computador del desarrollador a corvimet.cl, y cómo lo abre cada persona. El resumen de diseño está en [SSD §6](SSD.md).

---

## 1. En una imagen

```
PC del desarrollador ──git push──► GitHub (Iyov/corvimet.cl) ──Workers Builds──► Cloudflare ◄── NIC Chile: corvimet.cl apunta aquí
  wrangler dev                      código, historial y CI                          servidor: Worker + Static Assets + D1 + R2 + Access
  Flow sandbox                      (no sirve el sitio)                              preview (*.workers.dev) y producción (corvimet.cl)
```

- **No queda nada "en local".** Lo local es solo para desarrollar.
- **GitHub guarda el código**, el historial y ejecuta las verificaciones. No publica el sitio.
- **Cloudflare es el servidor.** Se actualiza solo con cada cambio aprobado en `main`.

## 2. Quién abre qué

| Persona | Dirección | Acceso |
|---|---|---|
| Clientes de Corvimet | `https://corvimet.cl` | Público |
| Administradores de Corvimet | `https://corvimet.cl/admin` | Correo + código de un solo uso (Cloudflare Access) |
| Cliente revisando una etapa | Enlace de preview `https://<versión>-corvimet.<subdominio>.workers.dev` | Cloudflare Access (solo correos invitados) |
| Desarrollador | `http://localhost:8787` (`wrangler dev`) · `http://127.0.0.1:8765` (fase 0, `tools/serve.py`) | Local |

## 3. Preparación (una sola vez)

### 3.1 Cuenta de Cloudflare
1. Crear la cuenta **a nombre de Corvimet** (con un correo del negocio). El desarrollador queda como miembro **Administrator** (decisión D14, pendiente de confirmar).
2. Activar **2FA** para todos los miembros.
3. Elegir el subdominio `*.workers.dev` de la cuenta.

### 3.2 Conectar el repositorio (Workers Builds)
1. Workers & Pages → **Create** → **Import a repository** → GitHub → `Iyov/corvimet.cl`.
2. Production branch: `main`. Build command: vacío en la fase 0 (`npm ci && npm run build` desde la etapa 4). Deploy command: `npx wrangler deploy`.
3. Activar **builds de ramas que no son de producción**, para que cada rama o PR genere una versión de preview.
4. En GitHub, mantener la protección de `main`: PR con el check `verify` en verde.

### 3.3 Recursos (etapa 4 en adelante)
```bash
npx wrangler d1 create corvimet-db            # copiar el database_id a wrangler.jsonc
npx wrangler d1 create corvimet-db-preview
npx wrangler r2 bucket create corvimet-media
npx wrangler d1 migrations apply corvimet-db-preview --remote
```
Bindings en `wrangler.jsonc` (ejemplo, se completa en la etapa 4):
```jsonc
{
  "main": "src/index.ts",
  "assets": { "directory": "./public/", "binding": "ASSETS", "not_found_handling": "404-page", "html_handling": "auto-trailing-slash" },
  "d1_databases": [{ "binding": "DB", "database_name": "corvimet-db", "database_id": "<id>", "migrations_dir": "migrations" }],
  "r2_buckets": [{ "binding": "MEDIA", "bucket_name": "corvimet-media" }],
  "triggers": { "crons": ["*/5 * * * *"] },
  "vars": { "FLOW_API_BASE": "https://www.flow.cl/api", "NOTIFY_EMAIL": "<correo de avisos>" },
  "env": { "preview": { "vars": { "FLOW_API_BASE": "https://sandbox.flow.cl/api" } } }
}
```

### 3.4 Secretos (nunca en el repo)
```bash
npx wrangler secret put FLOW_API_KEY         # lo ingresa el titular de Flow
npx wrangler secret put FLOW_SECRET_KEY      # lo ingresa el titular de Flow
npx wrangler secret put TURNSTILE_SECRET
```
- Las claves de **producción** de Flow las escribe el titular de la cuenta directamente en el prompt o en el panel. No se envían por correo ni por WhatsApp.
- Preview y local usan las claves **sandbox** de Flow.
- Local: archivo `.dev.vars` (en `.gitignore`).

### 3.5 Cloudflare Access (mantenedor y preview)
1. Zero Trust → Access → Applications → **Self-hosted**.
2. Aplicación "Mantenedor": dominio `corvimet.cl`, rutas `/admin*` y `/api/admin*`. Política **Allow** para la lista de correos de los administradores. Método: One-time PIN (o Google).
3. Aplicación "Preview": dominio `*.workers.dev` del proyecto. Política para el cliente y el desarrollador.
4. Copiar el **AUD** y el **team domain** a las variables `ACCESS_AUD` y `ACCESS_TEAM_DOMAIN`; el Worker valida el JWT.

## 4. Flujo diario de trabajo
1. `git switch -c etapa-2/fichas`
2. Desarrollar en local (`npx wrangler dev`; en la fase 0, `python tools/harden.py && python tools/serve.py`).
3. Verificar: `python tools/verify.py` · `npm test` (etapa 4 en adelante) · `node tools/check-browser.mjs …` (Chrome Canary, también con `MOBILE=1`).
4. `git push` y abrir el PR. CI corre las verificaciones y Workers Builds crea la **preview**.
5. Se comparte la URL de preview con el cliente; el cliente aprueba.
6. Merge a `main`, que **despliega a producción**.
7. Si algo falla: Workers → Deployments → **Rollback** a la versión anterior (o `npx wrangler rollback`).

Migraciones de D1: aplicar en preview, probar, y aplicar en producción **antes** del merge que las necesita:
```bash
npx wrangler d1 migrations apply corvimet-db --remote
```

## 5. Paso a producción con el dominio (una vez, al final)
Resumen; el runbook completo de 10 pasos, con correo y SEO, está en [03 §4](03-google-correo-migracion.md).
1. Exportar la zona DNS desde cPanelHost (incluye MX, SPF, DKIM y TXT).
2. Agregar `corvimet.cl` a Cloudflare e importar y revisar la zona.
3. Workers → corvimet → Settings → **Domains & Routes** → Custom Domain `corvimet.cl` (y `www`, con 301 a uno solo).
4. En **NIC Chile**, cambiar los NS a los dos que indique Cloudflare (lo hace el titular).
5. Día 0: verificar el sitio, la compra en producción de bajo monto, el correo y el sitemap en Search Console.
6. Mantener cPanelHost de respaldo 30 días como mínimo; luego darlo de baja.

## 6. Operación
| Tarea | Frecuencia | Cómo |
|---|---|---|
| Revisar pedidos con pago sin confirmar | Diaria (automatizable) | Mantenedor → Pedidos → "pendiente_pago" de más de 1 hora |
| Respaldo de D1 | Automático (Time Travel) + export semanal a R2 | Cron y `wrangler d1 export` |
| Actualizar dependencias | Cuando avise Dependabot | PR, CI en verde y merge |
| Renovar `security.txt` | Anual (`Expires`) | `config/security.txt` → `harden.py` |
| Revisar Search Console y GA4 | Semanal las primeras 8 semanas; mensual después | Comparar con la línea base |
| Revisar cabeceras | Tras cada cambio de CSP | securityheaders.com y Mozilla Observatory |

## 7. Costos de infraestructura
Con el tráfico esperado, todo cabe en el **plan gratuito** de Cloudflare (Workers, D1, R2 y Access hasta 50 usuarios; ver [SSD §6.5](SSD.md)). Fuera de Cloudflare:
- Dominio `.cl` en NIC Chile (lo paga el titular, como hoy).
- Comisiones de Flow por venta.
- Correo, si se elige Google Workspace ([03 §3](03-google-correo-migracion.md)).
