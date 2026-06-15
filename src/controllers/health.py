"""Health controller — computes the service health payload.

Kept free of transport concerns (HTTP/Kafka/etc.); :mod:`views.http` calls
:func:`get_health_payload` to render the ``/health`` endpoint.
"""

from __future__ import annotations

import time

from models.health import Health


class HealthService:
    """Compute the current health status.

    :param service_name: The identifying name of this rApp service instance.
    """

    def __init__(self, service_name: str) -> None:
        self._service_name = service_name

    def get_health(self) -> Health:
        """Build and return the current health status.

        :return: :class:`~models.health.Health` with status ``"OK"`` and the
            current Unix timestamp.
        """
        return Health(status="OK", service=self._service_name, timestamp=int(time.time()))


def get_health_payload(health: HealthService) -> dict[str, object]:
    """Build the JSON-serializable health response payload.

    :param health: The :class:`HealthService` to query.
    :return: Dict with ``status``, ``service``, and ``timestamp`` fields.
    """
    return health.get_health().to_dict()
