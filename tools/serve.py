"""Servidor local que imita Cloudflare Workers Static Assets: aplica public/_headers,
auto-trailing-slash y 404.html. Uso: python tools/serve.py [puerto]"""
import fnmatch, os, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, unquote

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public")


def load_rules():
    rules, cur = [], None
    with open(os.path.join(ROOT, "_headers"), encoding="utf-8") as f:
        for line in f:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if not line[0].isspace():
                cur = (line.strip(), []); rules.append(cur)
            elif cur and ":" in line:
                k, v = line.strip().split(":", 1)
                cur[1].append((k.strip(), v.strip()))
    return rules


RULES = load_rules()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def end_headers(self):
        path = urlsplit(self.path).path
        merged = {}
        for pattern, headers in RULES:
            if fnmatch.fnmatch(path, pattern.replace(":splat", "*")):
                for k, v in headers:
                    merged[k] = f"{merged[k]}, {v}" if k in merged else v
        for k, v in merged.items():
            self.send_header(k, v)
        super().end_headers()

    def send_head(self):
        path = unquote(urlsplit(self.path).path)
        if path in ("/_headers",):
            self.send_error(404); return None
        full = os.path.join(ROOT, path.lstrip("/"))
        if path.endswith("/") and not os.path.exists(os.path.join(full, "index.html")) or \
                not path.endswith("/") and not os.path.exists(full) and not os.path.isdir(full):
            body = open(os.path.join(ROOT, "404.html"), "rb").read()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return None
        return super().send_head()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"http://localhost:{port}/")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
