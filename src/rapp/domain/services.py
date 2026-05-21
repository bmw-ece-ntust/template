from __future__ import annotations

import time

from .models import Health


class HealthService:
    """Domain service: compute health payload.

    Keep this free of transport concerns (HTTP/Kafka/etc.).

    :param service_name: The identifying name of this rApp service instance.
    """

    def __init__(self, service_name: str) -> None:
        self._service_name = service_name

    def get_health(self) -> Health:
        """Build and return the current health status.

        :return: :class:`Health` with status ``"OK"`` and current Unix timestamp.
        """
        return Health(status="OK", service=self._service_name, timestamp=int(time.time()))
