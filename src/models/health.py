from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Health:
    """Health status payload for the rApp service.

    :param status: Service health state (e.g. ``"OK"``).
    :param service: Name of the service reporting health.
    :param timestamp: Unix epoch time (seconds) of the health check.
    """

    status: str
    service: str
    timestamp: int

    def to_dict(self) -> dict[str, object]:
        """Serialize to a JSON-compatible dictionary.

        :return: Dictionary representation of the health payload.
        """
        return asdict(self)
