"""3GPP and O-RAN parameter identifier enumerations.

Using string enumerations eliminates typos, enables IDE auto-completion,
and makes the vendor-to-3GPP parameter mapping explicit and spec-traceable.

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from models.parameters import ThreeGPPKpi``.
"""

from __future__ import annotations

from models.parameters.node_type import NodeType
from models.parameters.three_gpp_kpi import ThreeGPPKpi
from models.parameters.vendor_parameter_map import VendorParameterMap

__all__ = [
    "NodeType",
    "ThreeGPPKpi",
    "VendorParameterMap",
]
