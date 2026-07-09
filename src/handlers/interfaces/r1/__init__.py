"""R1 interface adapters — Service Management Exposure (SME) and
Information Coordination Service (ICS / DME).

The R1 interface (O-RAN WG2 R1-AP) connects rApps to the Non-RT RIC
Service Management and Orchestration framework.  It has two key sub-services:

SME (Service Management Exposure)
    rApp lifecycle management: register services on startup, deregister on
    shutdown, and discover other rApps or enrichment-info producers.

ICS / DME (Information Coordination Service / Data Management Exposure)
    Data-as-a-service for rApps: subscribe to a typed data producer (e.g.
    cell-level KPM reports) and receive asynchronous push callbacks.

Adapter role
    Translates the Non-RT RIC REST APIs (O-RAN standard) to/from BMW Lab
    internal types.  :class:`SMEAdapter` manages the rApp service lifecycle;
    :class:`ICSAdapter` manages data subscriptions.

    .. code-block:: none

        [O-RAN R1 SME REST JSON] <── SMEAdapter ──> [rApp lifecycle state]
        [O-RAN R1 ICS REST JSON] <── ICSAdapter ──> [models.KpiReport]

OSC reference
    ``nonrtric/plt/rappmanager`` — ``threshold-control-rapp`` ``SMEClient``
    https://gerrit.o-ran-sc.org/r/gitweb?p=nonrtric/plt/rappmanager.git

Used by the OSC factory to register the rApp (SME) and subscribe to telemetry
(ICS) on startup.

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from handlers.interfaces.r1 import ICSAdapter, SMEAdapter``.

Pattern reference
    Adapter: https://refactoring.guru/design-patterns/adapter
"""

from __future__ import annotations

from handlers.interfaces.r1.ics_adapter import ICSAdapter
from handlers.interfaces.r1.ics_error import R1ICSError
from handlers.interfaces.r1.sme_adapter import SMEAdapter
from handlers.interfaces.r1.sme_error import R1SMEError

__all__ = [
    "ICSAdapter",
    "R1ICSError",
    "R1SMEError",
    "SMEAdapter",
]
