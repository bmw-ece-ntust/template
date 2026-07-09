"""rApp / xApp composition root.

Wires all layers and selects the deployment platform factory via
``RAPP_PLATFORM`` (default: ``osc``).

Platforms
    ``osc``   — O-RAN SC Non-RT RIC; pure 3GPP counter names, no translation.
    ``ns3``   — ns-3 simulation via ns-O-RAN (ns-O-RAN naming → 3GPP).
    ``viavi`` — VIAVI RIC Test / RSG (VIAVI naming → 3GPP, incl. PEE).
    ``oai``   — OpenAirInterface via FlexRIC (OAI naming → 3GPP).
    ``ocudu`` — Linux Foundation OCUDU (metric naming + units → 3GPP).

All platforms speak standard O-RAN interfaces; they differ only in the
KPI-name Adapter their factory produces.

Layout follows O-RAN SC nonrtric-rapp-healthcheck convention:
    runnable ``src/main.py`` with deps in ``src/requirements.txt``.
"""

from __future__ import annotations

import argparse
import logging

from config.logging import configure_logging
from config.settings import Settings
from controllers.health import HealthService
from controllers.kpi_controller import KpiController
from controllers.strategies import make_strategy
from factories import RAppPlatformFactory
from factories.ns3 import Ns3PlatformFactory
from factories.oai import OaiPlatformFactory
from factories.ocudu import OcuduPlatformFactory
from factories.osc import OscPlatformFactory
from factories.viavi import ViaviPlatformFactory
from views.http.server import serve_http

_log = logging.getLogger(__name__)

#: ``RAPP_PLATFORM`` → factory class.  Every entry shares the OSC O-RAN
#: transport constructor signature, so adding a vendor is one import and
#: one row — never a new ``if`` branch.
_FACTORY_BY_PLATFORM: dict[str, type[OscPlatformFactory]] = {
    "osc": OscPlatformFactory,
    "ns3": Ns3PlatformFactory,
    "viavi": ViaviPlatformFactory,
    "oai": OaiPlatformFactory,
    "ocudu": OcuduPlatformFactory,
}


def parse_args(defaults: Settings) -> Settings:
    """Parse CLI args, overriding env-var defaults where provided.

    :param defaults: :class:`~config.settings.Settings` from env.
    :return: Updated :class:`~config.settings.Settings`.
    """
    parser = argparse.ArgumentParser(prog="rapp-template")
    parser.add_argument("--host", default=defaults.host)
    parser.add_argument("--port", default=defaults.port, type=int)
    parser.add_argument("--service-name", default=defaults.service_name)
    parser.add_argument(
        "--platform",
        default=defaults.platform,
        choices=sorted(_FACTORY_BY_PLATFORM),
        help="Deployment platform (default: osc)",
    )
    parser.add_argument(
        "--strategy",
        default=defaults.strategy,
        help="Optimization strategy (default: threshold)",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1")
    args = parser.parse_args()
    return Settings(
        host=args.host,
        port=args.port,
        service_name=args.service_name,
        platform=args.platform,
        strategy=args.strategy,
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
    factory_class = _FACTORY_BY_PLATFORM.get(settings.platform)
    if factory_class is None:
        raise ValueError(
            f"Unknown RAPP_PLATFORM={settings.platform!r}. "
            f"Valid values: {', '.join(sorted(_FACTORY_BY_PLATFORM))}."
        )
    return factory_class(
        sme_base_url=settings.sme_base_url or "http://nonrtric:8090",
        ics_base_url=settings.ics_base_url or "http://nonrtric:8083",
        service_name=settings.service_name,
        instance_id=f"{settings.service_name}-01",
        callback_url=settings.callback_url or f"http://localhost:{settings.port}/r1/callback",
        cell_id=settings.cell_id,
    )


def main() -> None:
    """Entry point — wire all layers and start the HTTP server."""
    configure_logging()
    settings = parse_args(Settings.from_env())

    _log.info(
        "Starting rApp  platform=%s  service=%s  %s:%d",
        settings.platform,
        settings.service_name,
        settings.host,
        settings.port,
    )

    health_service = HealthService(service_name=settings.service_name)

    factory = _build_factory(settings)
    runner = factory.create_scenario_runner()
    controller = KpiController(
        collector=factory.create_telemetry_collector(),
        analyzer=factory.create_kpi_analyzer(),
        strategy=make_strategy(settings.strategy),
    )

    runner.start()

    # Demonstrate one control cycle at startup; a scheduler or ICS callback
    # would drive this loop in production.
    report, decision = controller.evaluate_once()
    _log.info("control cycle  cell=%s  decision=%s", report.cell_id, decision.value)

    try:
        serve_http(settings, health=health_service)
    finally:
        runner.stop()


if __name__ == "__main__":
    main()
