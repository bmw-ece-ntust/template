"""rApp / xApp composition root.

Wires all layers and selects the deployment environment factory via
``RAPP_PLATFORM`` (default: ``mock``).

Platforms
    ``mock``     — In-memory no-op components.  No external dependencies.
    ``osc``      — O-RAN SC Non-RT RIC (real or TA rApp simulation endpoint).
    ``physical`` — Physical gNB testbed with O-RAN management plane.

Layout follows O-RAN SC nonrtric-rapp-healthcheck convention:
    runnable ``src/main.py`` with deps in ``src/requirements.txt``.
"""

from __future__ import annotations

import argparse
import logging
import os

from factories import RAppPlatformFactory
from factories.mock import MockPlatformFactory
from rapp.adapters.http.server import serve_http
from rapp.config.settings import Settings
from rapp.domain.services import HealthService
from rapp.infrastructure.logging import configure_logging

_log = logging.getLogger(__name__)


def parse_args(defaults: Settings) -> Settings:
    """Parse CLI args, overriding env-var defaults where provided.

    :param defaults: :class:`~rapp.config.settings.Settings` from env.
    :return: Updated :class:`~rapp.config.settings.Settings`.
    """
    parser = argparse.ArgumentParser(prog="rapp-template")
    parser.add_argument("--host", default=defaults.host)
    parser.add_argument("--port", default=defaults.port, type=int)
    parser.add_argument("--service-name", default=defaults.service_name)
    parser.add_argument(
        "--platform",
        default=defaults.platform,
        choices=["mock", "osc", "physical"],
        help="Deployment platform (default: mock)",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1")
    args = parser.parse_args()
    return Settings(
        host=args.host,
        port=args.port,
        service_name=args.service_name,
        platform=args.platform,
        sme_base_url=defaults.sme_base_url,
        ics_base_url=defaults.ics_base_url,
        callback_url=defaults.callback_url,
        cell_id=defaults.cell_id,
        intent_secret=defaults.intent_secret,
    )


def _build_factory(settings: Settings) -> RAppPlatformFactory:
    """Select and construct the platform factory from ``settings.platform``.

    :param settings: Runtime settings.
    :return: Configured :class:`~factories.RAppPlatformFactory`.
    :raises ValueError: If ``settings.platform`` is unrecognized.
    """
    if settings.platform == "osc":
        from factories.osc import OscPlatformFactory
        return OscPlatformFactory(
            sme_base_url=settings.sme_base_url or "http://nonrtric:8090",
            ics_base_url=settings.ics_base_url or "http://nonrtric:8083",
            service_name=settings.service_name,
            instance_id=f"{settings.service_name}-01",
            callback_url=settings.callback_url or f"http://localhost:{settings.port}/r1/callback",
            cell_id=settings.cell_id,
        )

    if settings.platform == "physical":
        from factories.physical import PhysicalPlatformFactory
        return PhysicalPlatformFactory()

    if settings.platform == "mock":
        return MockPlatformFactory()

    raise ValueError(
        f"Unknown RAPP_PLATFORM={settings.platform!r}. "
        "Valid values: mock, osc, physical."
    )


def main() -> None:
    """Entry point — wire all layers and start the HTTP server."""
    configure_logging()
    settings = parse_args(Settings.from_env())

    _log.info(
        "Starting rApp  platform=%s  service=%s  %s:%d",
        settings.platform, settings.service_name, settings.host, settings.port,
    )

    health_service = HealthService(service_name=settings.service_name)

    factory = _build_factory(settings)
    runner   = factory.create_scenario_runner()
    collector = factory.create_telemetry_collector()  # noqa: F841 — used by xApp logic
    analyzer  = factory.create_kpi_analyzer()         # noqa: F841 — used by xApp logic

    runner.start()

    try:
        serve_http(settings, health_port=health_service)
    finally:
        runner.stop()


if __name__ == "__main__":
    main()
