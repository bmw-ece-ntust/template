"""O1 interface adapter — map O-RAN YANG operations to vendor NETCONF/REST.

The O1 interface (3GPP TS 28.535, O-RAN.WG5.O1) connects the SMO
(Service Management and Orchestration) to managed elements (gNBs) via
NETCONF/YANG.  In O-RAN SC deployments, O1 traffic is relayed through SDNC
(Software-Defined Network Controller).

Adapter role
    Translates vendor-proprietary YANG managed-object representations into
    O-RAN-standardised cell-configuration operations that application
    use-cases can call without any vendor knowledge.

    .. code-block:: none

        [Vendor-proprietary YANG MO] <── O1SdncAdapter ──> [O-RAN cell-config operations]

The :class:`O1Client` ABC defines the vendor-independent port contract.
Subclass it to support vendors whose YANG key names differ from the
``o-ran-sc-du-hello-world`` reference model.

OSC reference
    ``nonrtric/plt/rappmanager`` — ``threshold-control-rapp`` ``SDNCClient``
    https://gerrit.o-ran-sc.org/r/gitweb?p=nonrtric/plt/rappmanager.git

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from handlers.interfaces.o1 import O1SdncAdapter``.

Pattern reference
    Adapter: https://refactoring.guru/design-patterns/adapter
"""

from __future__ import annotations

from handlers.interfaces.o1.client import O1Client
from handlers.interfaces.o1.error import O1Error
from handlers.interfaces.o1.sdnc_adapter import O1SdncAdapter

__all__ = [
    "O1Client",
    "O1Error",
    "O1SdncAdapter",
]
