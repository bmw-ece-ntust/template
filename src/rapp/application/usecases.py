from __future__ import annotations

from rapp.application.ports import HealthPort


def get_health_payload(health_port: HealthPort) -> dict[str, object]:
    """Use-case: build the health response payload.

    :param health_port: Any object satisfying the
        :class:`~rapp.application.ports.HealthPort` protocol.
    :return: JSON-serializable dictionary with ``status``, ``service``,
        and ``timestamp`` fields.
    """

    return health_port.get_health().to_dict()
