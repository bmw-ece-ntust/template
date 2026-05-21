from __future__ import annotations

from typing import Protocol

from rapp.domain.models import Health


class HealthPort(Protocol):
    """Port (interface) for health-check operations.

    Any class implementing ``get_health()`` satisfies this protocol.
    """

    def get_health(self) -> Health:
        """Return the current health status of the service.

        :return: :class:`~rapp.domain.models.Health`
        """
        ...
