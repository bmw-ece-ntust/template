"""Identity record for a single network node (gNB cell or WiFi AP)."""

from __future__ import annotations

from dataclasses import dataclass

from models.parameters import NodeType


@dataclass(frozen=True)
class NodeInfo:
    """Identifies a single network node (gNB cell or WiFi AP).

    :param cell_id: NR Cell Global ID or AP BSSID / SSID.
    :param gnb_id: Parent gNB identifier (or AP cluster ID for WiFi).
    :param vendor_id: Vendor slug used to select the correct adapter
        (e.g. ``"viavi"``, ``"oai"``, ``"ocudu"``, ``"aruba"``).
    :param node_type: :class:`~models.parameters.NodeType`.
    :param is_active: ``True`` when the node is currently serving UEs.
    """

    cell_id: str
    gnb_id: str
    vendor_id: str
    node_type: NodeType = NodeType.GNB
    is_active: bool = True
