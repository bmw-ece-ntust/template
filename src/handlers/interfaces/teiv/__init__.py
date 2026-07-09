"""TEIV (Topology and Inventory) adapter — network topology discovery.

TEIV (O-RAN SC L Release) maintains a real-time graph of cells, gNBs,
O-DUs, O-RUs, and their relationships.  Use this adapter on startup to
populate :class:`~models.topology.NetworkTopology`, then subscribe to
O1 VES ``cellStatusChange`` events (via
:class:`~handlers.interfaces.ves.VesEventAdapter`) to keep it current.

rApps should not hard-code cell IDs.  Instead they query topology at startup
and iterate over :meth:`~models.topology.NetworkTopology.active_cells`.

OSC TEIV reference
    https://wiki.o-ran-sc.org/display/ORAN/Topology+Exposure+and+Inventory

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from handlers.interfaces.teiv import TEIVAdapter``.

Pattern reference
    Adapter: https://refactoring.guru/design-patterns/adapter
"""

from __future__ import annotations

from handlers.interfaces.teiv.adapter import TEIVAdapter
from handlers.interfaces.teiv.error import TEIVError

__all__ = [
    "TEIVAdapter",
    "TEIVError",
]
