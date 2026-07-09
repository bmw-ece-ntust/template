"""Network node type enum — selects the parameter mapping and adapter."""

from __future__ import annotations

from enum import Enum


class NodeType(str, Enum):
    """Network node type — selects the correct parameter mapping and adapter.

    :cvar GNB: 5G NR base station cell (gNB-DU / gNB-CU).
    :cvar ENODEB: 4G LTE eNodeB cell.
    :cvar WIFI_AP: IEEE 802.11 access point; mapped to 3GPP KPIs via O1 vendor adapter.
    """

    GNB = "gnb"
    ENODEB = "enodeb"
    WIFI_AP = "wifi_ap"
