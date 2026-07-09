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

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from handlers.interfaces.ves import VesEventAdapter``.

Pattern reference
    Adapter: https://refactoring.guru/design-patterns/adapter
"""

from __future__ import annotations

from handlers.interfaces.ves.common_header import VesCommonHeader
from handlers.interfaces.ves.error import VesError
from handlers.interfaces.ves.event import VesEvent
from handlers.interfaces.ves.event_adapter import VesEventAdapter
from handlers.interfaces.ves.event_type import VesEventType

__all__ = [
    "VesCommonHeader",
    "VesError",
    "VesEvent",
    "VesEventAdapter",
    "VesEventType",
]
