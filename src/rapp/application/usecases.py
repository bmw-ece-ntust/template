from __future__ import annotations

from rapp.application.ports import HealthPort


def get_health_payload(health_port: HealthPort) -> dict[str, object]:
    """Use-case: build the health response payload."""

    return health_port.get_health().to_dict()
