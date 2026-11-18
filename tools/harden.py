"""Construye public/ (sitio publicable y endurecido) a partir de la copia en bruto site/.

- Extrae todo <script> y <style> en línea a archivos con nombre por hash (assets/inline/),
  para que la CSP no necesite 'unsafe-inline' ni hashes.
- Elimina huellas de WordPress, emojis remotos, speculation rules y enlaces a feeds/API.
- Reescribe los recursos externos restantes (Google Fonts, Gravatar) a copias locales.
- Genera _headers (cabeceras de seguridad), robots.txt y .well-known/security.txt.

Uso: python tools/harden.py
"""
import hashlib, os, re, shutil, sys
from datetime import date, timedelta
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Comment

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mirror import local_rel, norm  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "site")
OUT = os.path.join(REPO, "public")
CONFIG = os.path.join(REPO, "config")
BASE = "https://corvimet.cl/"

# Rutas que no se publican (no aportan al sitio estático o filtran información)
EXCLUDE_DIRS = ("author",)  # /author/admin/ revela el usuario de WordPress
EXCLUDE_FILES = re.compile(r"^(_mirror_manifest\.json|wp-sitemap.*\.(xml|xsl)|robots\.txt)$")

ALLOWED_FRAME_HOSTS = ("maps.google.com", "www.google.com")
DROP_LINK_REL = {"edituri", "wlwmanifest", "pingback", "shortlink", "profile",
                 "https://api.w.org/", "dns-prefetch", "preconnect", "alternate"}

stats = {"scripts": 0, "styles": 0, "pages": 0, "removed": 0}


def h(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:20]


def strip_domain(t: str) -> str:
    t = re.sub(r"https?:\\/\\/(?:www\.)?corvimet\.cl", "", t)
    t = re.sub(r"(?:https?:)?//(?:www\.)?corvimet\.cl(?=[/\"'\s?#)<]|$)", "", t)
    t = re.sub(r"(?:https:)?//fonts\.gstatic\.com/", "/_ext/fonts.gstatic.com/", t)
    return re.sub(r"https?:/+(?=_ext/)", "/", t)  # restos "https:/_ext/" del mirror


def write_inline(text: str, ext: str) -> str:
    data = strip_domain(text).strip().encode("utf-8")
    name = f"{h(data)}.{ext}"
    path = os.path.join(OUT, "assets", "inline", name)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data + b"\n")
    return f"/assets/inline/{name}"


def localize(url: str, page_url: str):
    """Devuelve la ruta local (/...) de un recurso externo si existe en la copia."""
    if not url or url.startswith(("data:", "#", "mailto:", "tel:")):
        return None
    absu = urljoin(page_url, url)
    if not absu.startswith("http"):
        return None
    rel = local_rel(norm(absu))
    return rel if os.path.exists(os.path.join(SRC, *rel.lstrip("/").split("/"))) else None


def harden_html(path_in: str, path_out: str, page_url: str):
    with open(path_in, encoding="utf-8", errors="replace") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # 1. Huellas y metadatos de WordPress
    for m in soup.find_all("meta", attrs={"name": re.compile("^generator$", re.I)}):
        m.decompose(); stats["removed"] += 1
    for link in soup.find_all("link"):
        rels = {r.lower() for r in (link.get("rel") or [])}
        if rels & DROP_LINK_REL:
            link.decompose(); stats["removed"] += 1
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()

    # 2. Scripts: quitar emojis y speculationrules, externalizar los inline ejecutables
    for sc in soup.find_all("script"):
        stype = (sc.get("type") or "text/javascript").lower()
        sid = sc.get("id") or ""
        body = sc.string or sc.get_text() or ""
        if stype == "speculationrules" or sid.startswith(("wp-emoji", "wc-cart-fragments")) or \
                "cart-fragments" in (sc.get("src") or "") or \
                (stype == "module" and "wp-emoji" in body) or "wpemoji" in body.lower():
            sc.decompose(); stats["removed"] += 1; continue
        if sc.get("src"):
            loc = localize(sc["src"], page_url)
            if loc:
                sc["src"] = loc
            continue
        if stype in ("text/javascript", "application/javascript", "module", "text/ecmascript"):
            if not body.strip():
                sc.decompose(); continue
            new = soup.new_tag("script", src=write_inline(body, "js"))
            if stype == "module":
                new["type"] = "module"
            if sid:
                new["id"] = sid
            sc.replace_with(new); stats["scripts"] += 1
        # application/json, ld+json, text/template: son datos, la CSP no los bloquea

    # 3. <style> en línea -> hoja externa (mismo lugar = misma cascada)
    for st in soup.find_all("style"):
        css = st.get_text()
        if not css.strip():
            st.decompose(); continue
        attrs = {"rel": "stylesheet", "href": write_inline(css, "css")}
        if st.get("media"):
            attrs["media"] = st["media"]
        if st.get("id"):
            attrs["id"] = st["id"]
        st.replace_with(soup.new_tag("link", attrs=attrs)); stats["styles"] += 1

    # 4. Recursos externos -> locales; enlaces externos seguros
    for tag in soup.find_all(["link", "img", "source", "a", "iframe"]):
        for attr in ("href", "src"):
            v = tag.get(attr)
            if not v or not re.match(r"^(https?:)?//", v):
                continue
            if tag.name == "a":
                if "corvimet.cl" not in v:
                    rel = set(tag.get("rel") or []) | {"noopener", "noreferrer"}
                    tag["rel"] = sorted(rel)
                continue
            if tag.name == "iframe":
                host = re.sub(r"^(https?:)?//", "", v).split("/")[0]
                if host in ALLOWED_FRAME_HOSTS:
                    tag[attr] = "https:" + v if v.startswith("//") else v
                    tag["sandbox"] = "allow-scripts allow-same-origin allow-popups"
                    tag["referrerpolicy"] = "no-referrer"
                    tag["loading"] = "lazy"
                continue
            loc = localize(v, page_url)
            if loc:
                tag[attr] = loc
        for attr in ("srcset",):
            v = tag.get(attr)
            if v and "//" in v:
                parts = []
                for p in v.split(","):
                    bits = p.strip().split(" ", 1)
                    loc = localize(bits[0], page_url) if bits[0] else None
                    parts.append(" ".join([loc or bits[0]] + bits[1:]))
                tag[attr] = ", ".join(parts)

    html = str(soup)
    # 5. Dominio absoluto -> raíz relativa (incluye JSON escapado)
    html = re.sub(r"https?:\\/\\/(?:www\.)?corvimet\.cl", "", html)
    html = re.sub(r"(?:https?:)?//(?:www\.)?corvimet\.cl(?=[/\"'\s?#)<]|$)", "", html)
    os.makedirs(os.path.dirname(path_out), exist_ok=True)
    with open(path_out, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    stats["pages"] += 1


def copy_tree():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    for dp, dirs, files in os.walk(SRC):
        rel_dir = os.path.relpath(dp, SRC)
        top = rel_dir.split(os.sep)[0]
        if top in EXCLUDE_DIRS:
            continue
        for fn in files:
            if rel_dir == "." and EXCLUDE_FILES.match(fn):
                continue
            src = os.path.join(dp, fn)
            dst = os.path.join(OUT, rel_dir, fn)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if fn.endswith(".html"):
                url_path = "/" + rel_dir.replace(os.sep, "/").strip("./") + "/"
                url_path = url_path.replace("//", "/")
                harden_html(src, dst, urljoin(BASE, url_path.lstrip("/")))
            else:
                shutil.copy2(src, dst)
                # "font.woff2?5.11.0" se guardó como "font_<hash>.woff2"; un servidor estático
                # ignora la query, así que también se publica con el nombre original.
                m = re.match(r"^(.+)_[0-9a-f]{8}(\.[A-Za-z0-9]+)$", fn)
                if m and not os.path.exists(os.path.join(dp, m.group(1) + m.group(2))):
                    shutil.copy2(src, os.path.join(OUT, rel_dir, m.group(1) + m.group(2)))
                if fn.endswith(".css"):
                    fix_css(dst)


def fix_css(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        t = f.read()
    o = t
    t = strip_domain(t)
    if t != o:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(t)


def write_config_files():
    # _headers y robots.txt viven en config/ (editables) y se copian a public/
    for fn in ("_headers", "robots.txt"):
        shutil.copy2(os.path.join(CONFIG, fn), os.path.join(OUT, fn))
    wk = os.path.join(OUT, ".well-known")
    os.makedirs(wk, exist_ok=True)
    expires = (date.today() + timedelta(days=365)).isoformat() + "T00:00:00.000Z"
    with open(os.path.join(CONFIG, "security.txt"), encoding="utf-8") as f:
        sec = f.read().replace("{{EXPIRES}}", expires)
    with open(os.path.join(wk, "security.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(sec)


if __name__ == "__main__":
    copy_tree()
    write_config_files()
    print(f"public/ generado: {stats['pages']} páginas, {stats['scripts']} scripts y "
          f"{stats['styles']} estilos externalizados, {stats['removed']} elementos eliminados")
