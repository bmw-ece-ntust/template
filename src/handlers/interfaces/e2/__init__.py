"""E2 interface adapter stubs — SM-KPM and SM-RC.

The E2 interface connects Near-RT RIC xApps to RAN nodes (gNB-DU / gNB-CU).
Two E2 Service Models are used in most RAN optimization xApps:

E2SM-KPM (Key Performance Metrics)
    xApp subscribes to periodic KPM reports from the E2 node.  The Near-RT
    RIC forwards E2 Indication messages containing 3GPP PM counters.

E2SM-RC (RAN Control)
    xApp sends RIC Control Request messages to the E2 node to trigger
    actions: cell activation/deactivation, UE handover, resource control.

Adapter role
    Translates BMW Lab internal types to/from O-RAN E2 ASN.1 message
    structures.

    .. code-block:: none

        [E2 Indication (ASN.1/protobuf)] <── E2SmKpmAdapter ──> [KpiReport]
        [PolicyDecision]                 <── E2SmRcAdapter  ──> [E2 Control (ASN.1)]

Transport note
    Production deployments use RMR (O-RAN SC) or gRPC (FlexRIC) — neither
    uses HTTP.  :class:`E2Client` abstracts the transport so the xApp logic
    is independent of the underlying message bus.

O-RAN references
    E2AP:     O-RAN.WG3.E2AP-v03.01      https://specifications.o-ran.org/
    E2SM-KPM: O-RAN.WG3.E2SM-KPM-v03.00 https://specifications.o-ran.org/
    E2SM-RC:  O-RAN.WG3.E2SM-RC-v01.03  https://specifications.o-ran.org/

OSC xApp-frame-py reference
    https://gerrit.o-ran-sc.org/r/ric-plt/xapp-frame-py

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from handlers.interfaces.e2 import E2Client, E2SmKpmAdapter``.

Pattern reference
    Adapter: https://refactoring.guru/design-patterns/adapter
"""

from __future__ import annotations

from handlers.interfaces.e2.client import E2Client
from handlers.interfaces.e2.control_ack import E2ControlAck
from handlers.interfaces.e2.control_request import E2ControlRequest
from handlers.interfaces.e2.error import E2Error
from handlers.interfaces.e2.indication import E2Indication
from handlers.interfaces.e2.sm_kpm_adapter import E2SmKpmAdapter
from handlers.interfaces.e2.sm_rc_adapter import E2SmRcAdapter

__all__ = [
    "E2Client",
    "E2ControlAck",
    "E2ControlRequest",
    "E2Error",
    "E2Indication",
    "E2SmKpmAdapter",
    "E2SmRcAdapter",
]
