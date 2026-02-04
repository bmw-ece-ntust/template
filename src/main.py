"""Minimal rApp-style service entrypoint (composition root).

This repo keeps the O-RAN SC `nonrtric-rapp-healthcheck` convention:
- runnable `src/main.py`
- deps next to it in `src/requirements.txt`

Unlike a single-file demo, this entrypoint wires a small Clean/Hexagonal
structure under `src/rapp/`:
- domain: pure logic
- application: use-cases + ports
- adapters: HTTP and other integrations
"""

from __future__ import annotations

import argparse

from rapp.adapters.http.server import serve_http
from rapp.config.settings import Settings
from rapp.domain.services import HealthService
from rapp.infrastructure.logging import configure_logging


def parse_args(defaults: Settings) -> Settings:
    parser = argparse.ArgumentParser(prog="rapp-template")
    parser.add_argument("--host", default=defaults.host)
    parser.add_argument("--port", default=defaults.port, type=int)
    parser.add_argument("--service-name", default=defaults.service_name)
    parser.add_argument("--version", action="version", version="%(prog)s 0.1")
    args = parser.parse_args()
    return Settings(host=args.host, port=args.port, service_name=args.service_name)


def main() -> None:
    configure_logging()
    settings = parse_args(Settings.from_env())

    # Domain service(s) wired into application ports.
    health_service = HealthService(service_name=settings.service_name)

    # Adapters.
    serve_http(settings, health_port=health_service)


if __name__ == "__main__":
    main()