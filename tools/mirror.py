"""Mirror completo de https://corvimet.cl/ a ./site (servir con: python -m http.server -d site 8000)."""
import hashlib, os, re, sys, time, json
from collections import deque
from urllib.parse import urljoin, urlsplit, urlunsplit, unquote
import requests
from bs4 import BeautifulSoup

BASE = "https://corvimet.cl/"
HOST = "corvimet.cl"
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
DELAY = 0.15
ASSET_HOSTS_OK = True  # descargar recursos de terceros (fuentes, cdn)
SKIP_PAGE = re.compile(r"/wp-admin|/wp-login|xmlrpc\.php|/feed/?$|/wp-json|/comments/feed|"
                       r"add-to-cart=|replytocom=|\?s=|/embed/?$|/trackback|\.php\?", re.I)
ASSET_EXT = re.compile(r"\.(css|js|mjs|png|jpe?g|gif|webp|avif|svg|ico|woff2?|ttf|otf|eot|"
                       r"mp4|webm|mp3|pdf|json|xml|txt|map)$", re.I)

S = requests.Session()
S.headers["User-Agent"] = UA

done = {}          # url normalizada -> ruta local publicada (/...)
failed = {}
pages_q = deque()
assets_q = deque()
seen_pages, seen_assets = set(), set()


def norm(u):
    p = urlsplit(u)
    host = p.netloc.lower()
    if host == "www." + HOST:
        host = HOST
    return urlunsplit(("https", host, p.path or "/", p.query, ""))


def is_internal(u):
    return urlsplit(u).netloc.lower() in (HOST, "www." + HOST)


def local_rel(u, is_page=False):
    """Ruta publicada (empieza con /) para una URL."""
    p = urlsplit(u)
    path = unquote(p.path) or "/"
    prefix = "" if is_internal(u) else "/_ext/" + p.netloc.lower()
    q = p.query
    if is_page:
        if not path.endswith("/") and not re.search(r"\.html?$", path):
            path += "/"
        if path.endswith("/"):
            path += "index.html"
        if q:
            h = hashlib.md5(q.encode()).hexdigest()[:8]
            path = re.sub(r"(\.html?)$", f"_{h}\\1", path)
        return prefix + path
    if path.endswith("/"):
        path += "index"
    # ?ver=... no cambia el contenido -> se ignora; otras queries -> hash
    if q and not re.fullmatch(r"(ver|v)=[^&]*", q):
        h = hashlib.md5(q.encode()).hexdigest()[:8]
        base, ext = os.path.splitext(path)
        if not ext:
            ext = ".css" if "fonts.googleapis.com" in p.netloc else ""
        path = f"{base}_{h}{ext}"
    elif "fonts.googleapis.com" in p.netloc and not os.path.splitext(path)[1]:
        path += ".css"
    return prefix + path


def disk(rel):
    rel = rel.lstrip("/")
    rel = re.sub(r'[<>:"|?*]', "_", rel)
    return os.path.join(ROOT, *rel.split("/"))


def fetch(u):
    for attempt in range(3):
        try:
            time.sleep(DELAY)
            r = S.get(u, timeout=40, allow_redirects=True)
            return r
        except requests.RequestException as e:
            err = e
            time.sleep(2)
    failed[u] = str(err)
    return None


def add_page(u):
    u = norm(u)
    p = urlsplit(u)
    if not is_internal(u) or SKIP_PAGE.search(u):
        return
    if ASSET_EXT.search(p.path) or "/wp-content/" in p.path or "/wp-includes/" in p.path:
        return add_asset(u)
    if p.query and not re.fullmatch(r"(page_id|p|product_cat|paged|elementor_library)=[^&]*", p.query):
        return
    if u not in seen_pages:
        seen_pages.add(u)
        pages_q.append(u)


def add_asset(u):
    if u.startswith("data:") or u.startswith("blob:"):
        return
    u = norm(u)
    if not is_internal(u) and not ASSET_HOSTS_OK:
        return
    if u not in seen_assets:
        seen_assets.add(u)
        assets_q.append(u)


CSS_URL = re.compile(r"url\(\s*(['\"]?)([^)'\"]+)\1\s*\)|@import\s+(['\"])([^'\"]+)\3", re.I)
# URLs absolutas internas en texto/JSON (incluye https:\/\/corvimet.cl\/...)
ABS_INTERNAL = re.compile(r"https?:(?:\\?/){2}(?:www\.)?corvimet\.cl((?:\\?/)[^\s\"'<>()\\,]*(?:\\/[^\s\"'<>()\\,]*)*)", re.I)


def scan_css(text, base):
    for m in CSS_URL.finditer(text):
        ref = (m.group(2) or m.group(4) or "").strip()
        if ref and not ref.startswith(("data:", "#")):
            add_asset(urljoin(base, ref))


def scan_abs(text):
    for m in ABS_INTERNAL.finditer(text):
        path = m.group(1).replace("\\/", "/")
        u = "https://" + HOST + path
        if "/wp-content/" in path or "/wp-includes/" in path or ASSET_EXT.search(urlsplit(u).path):
            add_asset(u)
        else:
            add_page(u)


def scan_html(html, base):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(True):
        for attr in ("href", "src", "data-src", "data-lazy-src", "poster", "data-bg",
                     "data-background", "data-large_image", "data-thumb", "content", "action"):
            v = tag.get(attr)
            if not v or not isinstance(v, str):
                continue
            v = v.strip()
            if v.startswith(("mailto:", "tel:", "javascript:", "#", "data:", "whatsapp:")):
                continue
            if attr == "content" and not v.startswith(("http", "/")):
                continue
            u = urljoin(base, v)
            if not u.startswith("http"):
                continue
            name = tag.name
            if name == "a" or (name == "form" and attr == "action"):
                if is_internal(u):
                    add_page(u)
            elif name == "link":
                rel = " ".join(tag.get("rel") or [])
                if any(k in rel for k in ("stylesheet", "icon", "preload", "manifest", "apple-touch")):
                    add_asset(u)
                elif is_internal(u) and "alternate" not in rel and "shortlink" not in rel \
                        and "https://api.w.org/" not in rel and "pingback" not in rel:
                    add_page(u)
            elif name == "meta":
                if ASSET_EXT.search(urlsplit(u).path):
                    add_asset(u)
            elif name == "iframe":
                if is_internal(u):
                    add_page(u)
            else:
                add_asset(u)
        for attr in ("srcset", "data-srcset", "data-lazy-srcset", "imagesrcset"):
            v = tag.get(attr)
            if v:
                for part in v.split(","):
                    s = part.strip().split(" ")[0]
                    if s:
                        add_asset(urljoin(base, s))
        st = tag.get("style")
        if st:
            scan_css(st, base)
    for st in soup.find_all("style"):
        scan_css(st.get_text(), base)
    scan_abs(html)


def save(rel, content):
    path = disk(rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)


def crawl():
    # semillas: home + sitemaps
    add_page(BASE)
    r = fetch(BASE + "wp-sitemap.xml")
    if r is not None and r.ok:
        save("/wp-sitemap.xml", r.content)
        for sm in re.findall(r"<loc>([^<]+)</loc>", r.text):
            r2 = fetch(sm)
            if r2 is not None and r2.ok:
                save(local_rel(sm), r2.content)
                for loc in re.findall(r"<loc>([^<]+)</loc>", r2.text):
                    add_page(loc)
    for extra in ("robots.txt", "favicon.ico", "wp-sitemap-index.xsl", "wp-sitemap.xsl"):
        add_asset(BASE + extra)

    n = 0
    while pages_q or assets_q:
        if pages_q:
            u = pages_q.popleft()
            r = fetch(u)
            if r is None or r.status_code >= 400:
                failed[u] = r.status_code if r is not None else failed.get(u)
                continue
            final = norm(r.url)
            ctype = r.headers.get("Content-Type", "")
            if "html" not in ctype:
                rel = local_rel(final)
                save(rel, r.content); done[u] = rel
                continue
            rel = local_rel(final, is_page=True)
            done[u] = rel
            if final != u:
                done[final] = rel
                seen_pages.add(final)
            save(rel, r.content)
            scan_html(r.text, final)
            n += 1
            print(f"[page {n}] {u}  (cola: {len(pages_q)} pág / {len(assets_q)} rec)", flush=True)
        else:
            u = assets_q.popleft()
            headers = {}
            if "fonts.googleapis.com" in u:
                headers["User-Agent"] = UA
            r = fetch(u)
            if r is None or r.status_code >= 400:
                failed[u] = r.status_code if r is not None else failed.get(u)
                continue
            rel = local_rel(u)
            done[u] = rel
            save(rel, r.content)
            ctype = r.headers.get("Content-Type", "")
            path = urlsplit(u).path.lower()
            if "css" in ctype or path.endswith(".css") or "fonts.googleapis.com" in u:
                scan_css(r.text, u)
                scan_abs(r.text)
            elif "javascript" in ctype or path.endswith((".js", ".mjs", ".json")):
                scan_abs(r.text)

    with open(os.path.join(ROOT, "_mirror_manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"files": done, "failed": failed}, f, indent=1, ensure_ascii=False)
    print(f"\nDescargados: {len(done)}  Fallidos: {len(failed)}")


# ---------- reescritura de URLs para que funcione en local ----------
def rewrite():
    ext_map = {u: rel for u, rel in done.items() if not is_internal(u)}
    hashed = {u: rel for u, rel in done.items() if is_internal(u) and urlsplit(u).query}
    for dirpath, _, files in os.walk(ROOT):
        for fn in files:
            if not fn.endswith((".html", ".css", ".js", ".json", ".xml", ".htm")):
                continue
            fp = os.path.join(dirpath, fn)
            with open(fp, "rb") as f:
                raw = f.read()
            try:
                t = raw.decode("utf-8")
            except UnicodeDecodeError:
                continue
            orig = t
            # recursos externos -> /_ext/host/...
            for u, rel in sorted(ext_map.items(), key=lambda kv: -len(kv[0])):
                for variant in {u, u.replace("https:", ""), u.replace("&", "&amp;"),
                                u.replace("https:", "").replace("&", "&amp;"),
                                u.replace("/", "\\/")}:
                    t = t.replace(variant, rel if "\\/" not in variant else rel.replace("/", "\\/"))
            # internos con query significativa
            for u, rel in hashed.items():
                if fn.endswith((".html", ".htm")) and rel.endswith(".html"):
                    continue
                for variant in {u, u.replace("&", "&amp;")}:
                    t = t.replace(variant, rel)
            # dominio absoluto -> raíz relativa
            t = re.sub(r"https?:\\/\\/(?:www\.)?corvimet\.cl", "", t)
            t = re.sub(r"(?:https?:)?//(?:www\.)?corvimet\.cl(?=[/\"'\s?#)]|$)", "", t)
            # enlaces vacíos al home
            t = t.replace('href=""', 'href="/"')
            if t != orig:
                with open(fp, "w", encoding="utf-8", newline="") as f:
                    f.write(t)


if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    crawl()
    rewrite()
    print("Listo. Servir con: python -m http.server -d site 8000")
