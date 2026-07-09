"""VES CommonEventHeader value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VesCommonHeader:
    """VES CommonEventHeader fields (ONAP VES Listener 7.2 §5.4.1).

    :param domain: Event domain (see :class:`~handlers.interfaces.ves.VesEventType`).
    :param event_id: Unique event identifier.
    :param event_name: Structured event name (e.g. ``"Fault_Cell_Shutdown"``).
    :param source_name: Managed element ID (gNB node name / O-DU ID).
    :param source_id: VNF / network-element UUID.
    :param last_epoch_ms: Event time (Unix epoch milliseconds).
    :param sequence: Monotonically increasing event sequence number.
    """

    domain: str
    event_id: str
    event_name: str
    source_name: str
    source_id: str
    last_epoch_ms: int
    sequence: int = 0
