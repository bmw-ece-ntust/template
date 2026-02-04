from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler

from rapp.application.usecases import get_health_payload
from rapp.config.settings import Settings


def stats_html(settings: Settings, payload: dict[str, object]) -> str:
    return f"""<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv=\"refresh\" content=\"5\">
    <title>{settings.service_name} stats</title>
  </head>
  <body>
    <h3>Service</h3>
    <pre>{json.dumps(payload, indent=2)}</pre>
    <p>Endpoints: <code>/health</code>, <code>/status</code>, <code>/stats</code></p>
  </body>
</html>
"""


def make_handler(settings: Settings, *, health_port) -> type[BaseHTTPRequestHandler]:
    """Create a request handler bound to app dependencies."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path in ("/", "/health", "/status"):
                payload = get_health_payload(health_port)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(payload).encode("utf-8"))
                return

            if self.path == "/stats":
                payload = get_health_payload(health_port)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(stats_html(settings, payload).encode("utf-8"))
                return

            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "NOT_FOUND"}).encode("utf-8"))

        def log_message(self, fmt: str, *args: object) -> None:
            # Keep the default behavior but make it explicit.
            print(f"[http] {self.address_string()} - {fmt % args}")

    return Handler
