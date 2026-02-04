from __future__ import annotations

import time

from .models import Health


class HealthService:
    """Domain service: compute health payload.

    Keep this free of transport concerns (HTTP/Kafka/etc.).
    """

    def __init__(self, service_name: str) -> None:
        self._service_name = service_name

    def get_health(self) -> Health:
        return Health(status="OK", service=self._service_name, timestamp=int(time.time()))
