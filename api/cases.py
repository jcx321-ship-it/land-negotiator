"""Vercel Python function: /api/cases"""
import json, os, sys
from http.server import BaseHTTPRequestHandler
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import webapi  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        self._send(*webapi.get("/api/cases"))

    def do_POST(self):
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except ValueError as e:
            return self._send(400, {"error": str(e)})
        self._send(*webapi.post("/api/cases", req))
