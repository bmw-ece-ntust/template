from __future__ import annotations

from http.server import HTTPServer

from rapp.adapters.http.api import make_handler
from rapp.config.settings import Settings


def serve_http(settings: Settings, *, health_port) -> None:
    """Run the HTTP server (blocking)."""

    server = HTTPServer((settings.host, settings.port), make_handler(settings, health_port=health_port))
    print(
        f"Serving on http://{settings.host}:{settings.port} "
        f"(health: /health, stats: /stats)"
    )
    server.serve_forever()
