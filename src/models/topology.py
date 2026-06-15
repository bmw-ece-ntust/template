"""Network topology domain model — multi-gNB / multi-vendor / WiFi registry.

Populated from the SMO TEIV service (:class:`~handlers.teiv.TEIVAdapter`)
or configured manually.  Use-cases iterate over :class:`NetworkTopology` when
applying operations across multiple cells or gNBs.
"""

from __future__ import annotations

from dataclasses import dataclass

from models.parameters import NodeType


@dataclass(frozen=True)
class NodeInfo:
    """Identifies a single network node (gNB cell or WiFi AP).

    :param cell_id: NR Cell Global ID or AP BSSID / SSID.
    :param gnb_id: Parent gNB identifier (or AP cluster ID for WiFi).
    :param vendor_id: Vendor slug used to select the correct adapter
        (e.g. ``"ericsson"``, ``"nokia"``, ``"aruba"``).
    :param node_type: :class:`~models.parameters.NodeType`.
    :param is_active: ``True`` when the node is currently serving UEs.
    """

    cell_id: str
    gnb_id: str
    vendor_id: str
    node_type: NodeType = NodeType.GNB
    is_active: bool = True


class NetworkTopology:
    """Registry of known network nodes for multi-gNB use-cases.

    Populated from TEIV on startup, then kept current via O1 VES
    ``cellStatusChange`` events.  Use-cases call :meth:`active_cells`
    to iterate over targets without hard-coding cell IDs.

    :Example:

        >>> topo = NetworkTopology()
        >>> topo.add(NodeInfo("cell-0", "gnb-1", "ericsson"))
        >>> topo.add(NodeInfo("ap-1",   "ap-cluster-a", "aruba", NodeType.WIFI_AP))
        >>> for node in topo.active_cells():
        ...     adapter.get_kpi_report(node.cell_id)
    """

    def __init__(self) -> None:
        self._nodes: dict[str, NodeInfo] = {}

    def add(self, node: NodeInfo) -> None:
        """Register a node.

        :param node: :class:`NodeInfo` to register.
        """
        self._nodes[node.cell_id] = node

    def remove(self, cell_id: str) -> None:
        """Deregister a node.

        :param cell_id: Cell to remove.  No-op if not found.
        """
        self._nodes.pop(cell_id, None)

    def get(self, cell_id: str) -> NodeInfo | None:
        """Look up a node by cell ID.

        :param cell_id: Cell to look up.
        :return: :class:`NodeInfo` or ``None`` if not registered.
        """
        return self._nodes.get(cell_id)

    def set_active(self, cell_id: str, *, active: bool) -> None:
        """Update the active state of a node in-place.

        :param cell_id: Cell to update.
        :param active: New active state.
        """
        node = self._nodes.get(cell_id)
        if node is not None:
            self._nodes[cell_id] = NodeInfo(
                cell_id=node.cell_id,
                gnb_id=node.gnb_id,
                vendor_id=node.vendor_id,
                node_type=node.node_type,
                is_active=active,
            )

    def cells(self, node_type: NodeType | None = None) -> list[NodeInfo]:
        """Return all registered nodes, optionally filtered by type.

        :param node_type: Return only nodes of this type when specified.
        :return: List of :class:`NodeInfo`.
        """
        nodes = list(self._nodes.values())
        if node_type is not None:
            nodes = [n for n in nodes if n.node_type == node_type]
        return nodes

    def active_cells(self, node_type: NodeType | None = None) -> list[NodeInfo]:
        """Return only active nodes, optionally filtered by type.

        :param node_type: Return only nodes of this type when specified.
        :return: List of active :class:`NodeInfo`.
        """
        return [n for n in self.cells(node_type) if n.is_active]
