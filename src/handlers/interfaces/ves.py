"""VES (Virtual Event Streaming) event adapter — inbound O1 event handler.

In O-RAN SC deployments, VES events flow:

    gNB VES Agent → SMO VES Collector → Kafka → ICS data producer
    → rApp (via ICS subscription callback)

The rApp receives data via the ICS subscription callback URL.  This adapter
parses the VES event payloads delivered to that endpoint so use-cases can
react to topology changes and fault events without querying the VES Collector
or InfluxDB directly.

Reference
    TS 28.532 (VES event schema):
        https://www.3gpp.org/ftp/Specs/archive/28_series/28.532/28532-i50.zip
    ONAP VES Listener API 7.2:
        https://docs.onap.org/projects/onap-vnfsdk-model/en/latest/

Pattern reference
    Adapter: https://refactoring.guru/design-patterns/adapter
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# VES event types
# ---------------------------------------------------------------------------


class VesEventType(str, Enum):
    """VES domain / event-type identifiers used in O-RAN SC deployments.

    Source: ONAP VES Listener 7.2 §5.4 (domain enumeration).
    """

    FAULT = "fault"
    MEASUREMENT = "measurement"
    NOTIFICATION = "notification"
    STATE_CHANGE = "stateChange"
    THRESHOLD_CROSSING = "thresholdCrossingAlert"


# ---------------------------------------------------------------------------
# VES event data structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VesCommonHeader:
    """VES CommonEventHeader fields (ONAP VES Listener 7.2 §5.4.1).

    :param domain: Event domain (see :class:`VesEventType`).
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


@dataclass(frozen=True)
class VesEvent:
    """Parsed VES event envelope.

    :param header: :class:`VesCommonHeader`.
    :param body: Domain-specific event payload (fault, measurement, etc.).
    """

    header: VesCommonHeader
    body: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# VES event adapter
# ---------------------------------------------------------------------------


class VesEventAdapter:
    """Parses and dispatches inbound VES event payloads.

    Receives the raw JSON dict delivered to the rApp's ICS callback URL
    (forwarded from the VES Collector via the ICS bridge), parses it into
    :class:`VesEvent` objects, and routes to registered handlers.

    :Example:

        >>> adapter = VesEventAdapter()
        >>> adapter.register(VesEventType.STATE_CHANGE, on_cell_state_change)
        >>> adapter.dispatch(raw_ves_json)  # call from ICS callback endpoint
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[[VesEvent], None]]] = {}

    def register(self, event_type: VesEventType, handler: Callable[[VesEvent], None]) -> None:
        """Register a handler for a VES event type.

        :param event_type: :class:`VesEventType` to handle.
        :param handler: Callable accepting a :class:`VesEvent`.
        """
        self._handlers.setdefault(event_type.value, []).append(handler)

    def dispatch(self, raw: dict[str, Any]) -> VesEvent | None:
        """Parse a raw VES JSON payload and invoke matching handlers.

        :param raw: Raw VES event dict (top-level ``{"event": {...}}``).
        :return: Parsed :class:`VesEvent`, or ``None`` if parsing fails.
        """
        try:
            event = self._parse(raw)
        except (KeyError, ValueError) as exc:
            _log.warning("VES parse failed: %s  raw=%r", exc, raw)
            return None

        for handler in self._handlers.get(event.header.domain, []):
            try:
                handler(event)
            except Exception:
                _log.exception("VES handler error for event %s", event.header.event_id)
        return event

    # --- Parsing helpers ----------------------------------------------------

    @staticmethod
    def _parse(raw: dict[str, Any]) -> VesEvent:
        """Parse a raw VES JSON dict into a :class:`VesEvent`.

        :param raw: Top-level VES payload ``{"event": {"commonEventHeader": {...}, ...}}``.
        :return: :class:`VesEvent`.
        :raises KeyError: If required header fields are missing.
        :raises ValueError: If field types are unexpected.
        """
        event_root = raw["event"]
        hdr = event_root["commonEventHeader"]
        header = VesCommonHeader(
            domain=hdr["domain"],
            event_id=hdr["eventId"],
            event_name=hdr["eventName"],
            source_name=hdr["sourceName"],
            source_id=hdr.get("sourceId", ""),
            last_epoch_ms=int(hdr["lastEpochMicrosec"]),
            sequence=int(hdr.get("sequence", 0)),
        )
        body = {k: v for k, v in event_root.items() if k != "commonEventHeader"}
        return VesEvent(header=header, body=body)


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class VesError(RuntimeError):
    """Raised when a VES event cannot be processed."""
