"""Local web server (stdlib only): serves the UI and the JSON API in webapi.py. On Vercel, api/*.py do the same."""
from __future__ import annotations
import json, os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import webapi

ROOT = os.path.dirname(os.path.abspath(__file__))


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._send(200, open(os.path.join(ROOT, "index.html"), "rb").read(), "text/html; charset=utf-8")
        self._send(*webapi.get(self.path))

    def do_POST(self):
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except ValueError as e:
            return self._send(400, {"error": str(e)})
        self._send(*webapi.post(self.path, req))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "7860"))
    print(f"Land Negotiator on http://0.0.0.0:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()
