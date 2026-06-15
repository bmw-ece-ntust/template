from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime settings read exclusively from environment variables.

    Env var precedence: ``RAPP_*`` overrides legacy names. Each field below
    lists its environment variable, legacy fallback, and default.

    :param host: ``RAPP_HOST`` (legacy ``HOST``); default ``0.0.0.0`` — bind address.
    :param port: ``RAPP_PORT`` (legacy ``PORT``); default ``8080`` — listen port.
    :param service_name: ``RAPP_SERVICE_NAME`` (legacy ``SERVICE_NAME``);
        default ``template-app`` — service name in the health payload.
    :param platform: ``RAPP_PLATFORM``; default ``mock`` —
        factory selector (``mock`` / ``osc`` / ``physical``).
    :param strategy: ``RAPP_STRATEGY``; default ``threshold`` —
        optimization-algorithm selector (see :func:`controllers.strategies.make_strategy`).
    :param sme_base_url: ``RAPP_SME_BASE_URL`` — Non-RT RIC SME base URL (osc mode).
    :param ics_base_url: ``RAPP_ICS_BASE_URL`` — Non-RT RIC ICS base URL (osc mode).
    :param callback_url: ``RAPP_CALLBACK_URL`` — this rApp's callback URL (osc mode).
    :param cell_id: ``RAPP_CELL_ID``; default ``cell-0`` — primary cell ID (osc mode).
    :param intent_secret: ``RAPP_INTENT_SECRET`` — HMAC secret for IBN intent contracts.
    """

    host: str = "0.0.0.0"
    port: int = 8080
    service_name: str = "template-app"
    platform: str = "mock"
    strategy: str = "threshold"
    sme_base_url: str = ""
    ics_base_url: str = ""
    callback_url: str = ""
    cell_id: str = "cell-0"
    intent_secret: str = ""

    @staticmethod
    def from_env() -> Settings:
        """Build a :class:`Settings` instance from environment variables.

        :return: Populated :class:`Settings`.
        """
        host = os.getenv("RAPP_HOST") or os.getenv("HOST") or "0.0.0.0"
        port_raw = os.getenv("RAPP_PORT") or os.getenv("PORT") or "8080"
        service_name = os.getenv("RAPP_SERVICE_NAME") or os.getenv("SERVICE_NAME") or "template-app"
        platform = os.getenv("RAPP_PLATFORM", "mock").lower()
        strategy = os.getenv("RAPP_STRATEGY", "threshold").lower()

        try:
            port = int(port_raw)
        except ValueError:
            port = 8080

        return Settings(
            host=host,
            port=port,
            service_name=service_name,
            platform=platform,
            strategy=strategy,
            sme_base_url=os.getenv("RAPP_SME_BASE_URL", ""),
            ics_base_url=os.getenv("RAPP_ICS_BASE_URL", ""),
            callback_url=os.getenv("RAPP_CALLBACK_URL", ""),
            cell_id=os.getenv("RAPP_CELL_ID", "cell-0"),
            intent_secret=os.getenv("RAPP_INTENT_SECRET", ""),
        )
