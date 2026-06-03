from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime settings read exclusively from environment variables.

    Env var precedence: ``RAPP_*`` overrides legacy names.

    | Env var              | Legacy         | Default          | Description                        |
    |----------------------|----------------|------------------|------------------------------------|
    | ``RAPP_HOST``        | ``HOST``       | ``0.0.0.0``      | Bind address                       |
    | ``RAPP_PORT``        | ``PORT``       | ``8080``         | Listen port                        |
    | ``RAPP_SERVICE_NAME``| ``SERVICE_NAME``| ``template-app`` | Service name in health payload     |
    | ``RAPP_PLATFORM``    | —              | ``mock``         | Factory: mock / osc / physical     |
    | ``RAPP_SME_BASE_URL``| —              | —                | Non-RT RIC SME base URL (osc mode) |
    | ``RAPP_ICS_BASE_URL``| —              | —                | Non-RT RIC ICS base URL (osc mode) |
    | ``RAPP_CALLBACK_URL``| —              | —                | This rApp's callback URL (osc mode)|
    | ``RAPP_CELL_ID``     | —              | ``cell-0``       | Primary cell ID (osc mode)         |
    | ``RAPP_INTENT_SECRET``| —             | —                | HMAC secret for IBN intent contracts|
    """

    host: str = "0.0.0.0"
    port: int = 8080
    service_name: str = "template-app"
    platform: str = "mock"
    sme_base_url: str = ""
    ics_base_url: str = ""
    callback_url: str = ""
    cell_id: str = "cell-0"
    intent_secret: str = ""

    @staticmethod
    def from_env() -> "Settings":
        """Build a :class:`Settings` instance from environment variables.

        :return: Populated :class:`Settings`.
        """
        host = os.getenv("RAPP_HOST") or os.getenv("HOST") or "0.0.0.0"
        port_raw = os.getenv("RAPP_PORT") or os.getenv("PORT") or "8080"
        service_name = (
            os.getenv("RAPP_SERVICE_NAME") or os.getenv("SERVICE_NAME") or "template-app"
        )
        platform = os.getenv("RAPP_PLATFORM", "mock").lower()

        try:
            port = int(port_raw)
        except ValueError:
            port = 8080

        return Settings(
            host=host,
            port=port,
            service_name=service_name,
            platform=platform,
            sme_base_url=os.getenv("RAPP_SME_BASE_URL", ""),
            ics_base_url=os.getenv("RAPP_ICS_BASE_URL", ""),
            callback_url=os.getenv("RAPP_CALLBACK_URL", ""),
            cell_id=os.getenv("RAPP_CELL_ID", "cell-0"),
            intent_secret=os.getenv("RAPP_INTENT_SECRET", ""),
        )
