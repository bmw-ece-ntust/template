from __future__ import annotations

from http.server import HTTPServer

from config.settings import Settings
from controllers.health import HealthService
from views.http.api import make_handler


def serve_http(settings: Settings, *, health: HealthService) -> None:
    """Run the HTTP server (blocking).

    :param settings: Application settings (host, port, service name).
    :param health: The :class:`~controllers.health.HealthService` to expose.
    """
    server = HTTPServer((settings.host, settings.port), make_handler(settings, health=health))
    print(f"Serving on http://{settings.host}:{settings.port} (health: /health, stats: /stats)")
    server.serve_forever()
