import json
import os
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
UPSTREAM = "https://api.mail.tm"


def set_cors(handler):
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, Accept")
    handler.send_header("Access-Control-Max-Age", "86400")


class AppHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_OPTIONS(self):
        self.send_response(204)
        set_cors(self)
        self.end_headers()

    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def _handle_request(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parsed.query

        if path.startswith("/api/"):
            self._proxy_upstream(path[len("/api"):], query, self.command)
            return

        if path == "/":
            file_path = ROOT / "index.html"
        else:
            file_path = ROOT / path.lstrip("/")

        if file_path.exists() and file_path.is_file():
            self._serve_file(file_path)
            return

        self.send_error(404, "Not found")

    def _proxy_upstream(self, upstream_path, query, method):
        url = f"{UPSTREAM}{upstream_path}"
        if query:
            url = f"{url}?{query}"

        headers = {"Accept": "application/json"}
        payload = None

        if "Content-Type" in self.headers:
            headers["Content-Type"] = self.headers["Content-Type"]

        if "Authorization" in self.headers:
            headers["Authorization"] = self.headers["Authorization"]

        if method == "POST":
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = self.rfile.read(content_length) if content_length else b""

        req = urllib.request.Request(url, data=payload, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
                status = resp.status
                content_type = resp.headers.get_content_type()
                self.send_response(status)
                set_cors(self)
                self.send_header("Content-Type", content_type + "; charset=utf-8" if content_type else "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                if body:
                    self.wfile.write(body)
        except urllib.error.HTTPError as e:
            body = e.read()
            self.send_response(e.code)
            set_cors(self)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)
        except Exception as exc:
            payload = json.dumps({"error": str(exc)}).encode("utf-8")
            self.send_response(502)
            set_cors(self)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    def _serve_file(self, file_path):
        try:
            data = file_path.read_bytes()
        except OSError:
            self.send_error(404, "File not found")
            return

        content_type = "text/html; charset=utf-8"
        if file_path.suffix.lower() == ".css":
            content_type = "text/css; charset=utf-8"
        elif file_path.suffix.lower() == ".js":
            content_type = "application/javascript; charset=utf-8"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), AppHandler)
    print(f"Serving DAHORD'Mailer on http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
