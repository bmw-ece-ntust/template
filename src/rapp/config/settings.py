from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime settings.

    Env vars support both `RAPP_*` (preferred) and legacy names for compatibility.
    """

    host: str = "0.0.0.0"
    port: int = 8080
    service_name: str = "template-app"

    @staticmethod
    def from_env() -> "Settings":
        host = os.getenv("RAPP_HOST") or os.getenv("HOST") or "0.0.0.0"
        port_raw = os.getenv("RAPP_PORT") or os.getenv("PORT") or "8080"
        service_name = os.getenv("RAPP_SERVICE_NAME") or os.getenv("SERVICE_NAME") or "template-app"

        try:
            port = int(port_raw)
        except ValueError:
            port = 8080

        return Settings(host=host, port=port, service_name=service_name)
