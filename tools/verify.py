"""Verificación estática de public/ (se ejecuta en CI). Sale con código 1 si algo falla.

Comprueba: sin scripts/estilos/handlers en línea, sin recursos de terceros no permitidos,
todas las referencias locales existen, _headers dentro de los límites de Cloudflare y
con las cabeceras obligatorias, sin huellas de WordPress.
"""
import os, re, sys
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public")
ALLOWED_FRAMES = ("https://maps.google.com/", "https://www.google.com/")
REQUIRED_HEADERS = ("Content-Security-Policy", "Strict-Transport-Security", "X-Content-Type-Options",
                    "Referrer-Policy", "Permissions-Policy", "Cross-Origin-Opener-Policy",
                    "X-Frame-Options")
# Recursos que también dan 404 en el sitio original (no son errores de la copia)
KNOWN_MISSING = ("images/shade.png", "particles/particles.min.js")
EXEC_TYPES =("", "text/javascript", "application/javascript", "module", "text/ecmascript")
errors = []


def err(msg):
    errors.append(msg)


def exists(ref, base_dir):
    p = unquote(urlsplit(ref).path)
    if not p or p.endswith(KNOWN_MISSING):
        return True
    full = os.path.join(ROOT, p.lstrip("/")) if p.startswith("/") else os.path.join(base_dir, p)
    full = os.path.normpath(full)
    return os.path.isfile(full) or os.path.isfile(os.path.join(full, "index.html"))


def check_headers():
    path = os.path.join(ROOT, "_headers")
    if not os.path.exists(path):
        return err("falta public/_headers")
    lines = open(path, encoding="utf-8").read().splitlines()
    rules = [l for l in lines if l and not l[0].isspace() and not l.startswith("#")]
    if len(rules) > 100:
        err(f"_headers: {len(rules)} reglas (> 100)")
    for i, l in enumerate(lines, 1):
        if len(l) > 2000:
            err(f"_headers:{i}: {len(l)} caracteres (> 2000)")
    text = "\n".join(lines)
    for h in REQUIRED_HEADERS:
        if f"{h}:" not in text:
            err(f"_headers: falta {h}")
    csp = re.search(r"Content-Security-Policy:(.*)", text)
    if csp and "'unsafe-inline'" in csp.group(1).replace("style-src-attr 'unsafe-inline'", ""):
        err("CSP: 'unsafe-inline' fuera de style-src-attr")
    if csp and "'unsafe-eval'" in csp.group(1):
        err("CSP: contiene 'unsafe-eval'")


def check_html(fp):
    rel = os.path.relpath(fp, ROOT)
    base_dir = os.path.dirname(fp)
    soup = BeautifulSoup(open(fp, encoding="utf-8").read(), "html.parser")
    if soup.find("meta", attrs={"name": "generator"}):
        err(f"{rel}: meta generator")
    for sc in soup.find_all("script"):
        if not sc.get("src") and (sc.get("type") or "").lower() in EXEC_TYPES and (sc.string or "").strip():
            err(f"{rel}: <script> en línea")
    if soup.find("style"):
        err(f"{rel}: <style> en línea")
    for tag in soup.find_all(True):
        for a in tag.attrs:
            if a.lower().startswith("on"):
                err(f"{rel}: handler en línea {tag.name}.{a}")
    for tag in soup.find_all(["script", "link", "img", "source", "iframe", "video", "audio"]):
        refs = [tag.get("src"), tag.get("href") if tag.name == "link" else None]
        for s in (tag.get("srcset") or "").split(","):
            refs.append(s.strip().split(" ")[0] if s.strip() else None)
        for ref in filter(None, refs):
            if ref.startswith("data:"):
                continue
            if re.match(r"^(https?:)?//", ref):
                if tag.name == "iframe" and ref.startswith(ALLOWED_FRAMES):
                    continue
                if tag.name == "link" and "canonical" in (tag.get("rel") or []):
                    continue
                err(f"{rel}: recurso externo {tag.name} {ref[:100]}")
            elif not exists(ref, base_dir):
                err(f"{rel}: no existe {ref[:120]}")


def check_css(fp):
    rel = os.path.relpath(fp, ROOT)
    t = open(fp, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r"url\(\s*['\"]?([^)'\"]+)", t):
        ref = m.group(1).strip()
        if ref.startswith(("data:", "#", "%23")):
            continue
        if re.match(r"^(https?:)?//", ref):
            err(f"{rel}: url() externa {ref[:100]}")
        elif not exists(ref, os.path.dirname(fp)):
            err(f"{rel}: no existe {ref[:120]}")


if __name__ == "__main__":
    check_headers()
    n = 0
    for dp, _, files in os.walk(ROOT):
        for fn in files:
            fp = os.path.join(dp, fn)
            if fn.endswith(".html"):
                check_html(fp); n += 1
            elif fn.endswith(".css"):
                check_css(fp)
    for e in sorted(set(errors))[:200]:
        print("ERROR", e)
    print(f"{n} páginas revisadas, {len(set(errors))} errores")
    sys.exit(1 if errors else 0)
