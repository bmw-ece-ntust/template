"""Network topology domain model — multi-gNB / multi-vendor / WiFi registry.

Populated from the SMO TEIV service (:class:`~handlers.interfaces.teiv.TEIVAdapter`)
or configured manually.  Use-cases iterate over :class:`NetworkTopology` when
applying operations across multiple cells or gNBs.

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from models.topology import NetworkTopology, NodeInfo``.
"""

from __future__ import annotations

from models.topology.network_topology import NetworkTopology
from models.topology.node_info import NodeInfo

__all__ = [
    "NetworkTopology",
    "NodeInfo",
]
