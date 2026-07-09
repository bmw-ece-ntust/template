"""Parsing and dispatch of inbound VES event payloads."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from handlers.interfaces.ves.common_header import VesCommonHeader
from handlers.interfaces.ves.event import VesEvent
from handlers.interfaces.ves.event_type import VesEventType

_log = logging.getLogger(__name__)


class VesEventAdapter:
    """Parses and dispatches inbound VES event payloads.

    Receives the raw JSON dict delivered to the rApp's ICS callback URL
    (forwarded from the VES Collector via the ICS bridge), parses it into
    :class:`~handlers.interfaces.ves.VesEvent` objects, and routes to
    registered handlers.

    :Example:

        >>> adapter = VesEventAdapter()
        >>> adapter.register(VesEventType.STATE_CHANGE, on_cell_state_change)
        >>> adapter.dispatch(raw_ves_json)  # call from ICS callback endpoint
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[[VesEvent], None]]] = {}

    def register(self, event_type: VesEventType, handler: Callable[[VesEvent], None]) -> None:
        """Register a handler for a VES event type.

        :param event_type: :class:`~handlers.interfaces.ves.VesEventType` to handle.
        :param handler: Callable accepting a :class:`~handlers.interfaces.ves.VesEvent`.
        """
        self._handlers.setdefault(event_type.value, []).append(handler)

    def dispatch(self, raw: dict[str, Any]) -> VesEvent | None:
        """Parse a raw VES JSON payload and invoke matching handlers.

        :param raw: Raw VES event dict (top-level ``{"event": {...}}``).
        :return: Parsed :class:`~handlers.interfaces.ves.VesEvent`, or
            ``None`` if parsing fails.
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
        """Parse a raw VES JSON dict into a :class:`~handlers.interfaces.ves.VesEvent`.

        :param raw: Top-level VES payload ``{"event": {"commonEventHeader": {...}, ...}}``.
        :return: :class:`~handlers.interfaces.ves.VesEvent`.
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
