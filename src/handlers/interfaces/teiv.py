"""TEIV (Topology and Inventory) adapter — network topology discovery.

TEIV (O-RAN SC L Release) maintains a real-time graph of cells, gNBs,
O-DUs, O-RUs, and their relationships.  Use this adapter on startup to
populate :class:`~models.topology.NetworkTopology`, then subscribe to
O1 VES ``cellStatusChange`` events (via :class:`~handlers.interfaces.ves.VesEventAdapter`)
to keep it current.

rApps should not hard-code cell IDs.  Instead they query topology at startup
and iterate over :meth:`~models.topology.NetworkTopology.active_cells`.

:param teiv_base_url: TEIV REST API base URL
    (e.g. ``http://teiv.nonrtric.svc.cluster.local:8081``).

OSC TEIV reference
    https://wiki.o-ran-sc.org/display/ORAN/Topology+Exposure+and+Inventory
"""

from __future__ import annotations

import logging
from typing import Any

import requests

from models.parameters import NodeType
from models.topology import NetworkTopology, NodeInfo

_log = logging.getLogger(__name__)


class TEIVAdapter:
    """Queries the SMO TEIV service and populates a :class:`NetworkTopology`.

    :param teiv_base_url: TEIV REST API base URL.

    :Example:

        >>> adapter = TEIVAdapter("http://teiv.nonrtric.svc:8081")
        >>> topo = adapter.load_topology()
        >>> for node in topo.active_cells():
        ...     print(node.cell_id, node.vendor_id)
    """

    _CELLS_PATH = "/topology/v1/cells"

    def __init__(self, teiv_base_url: str) -> None:
        self._base = teiv_base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    def load_topology(self) -> NetworkTopology:
        """Fetch all cells from TEIV and return a populated :class:`NetworkTopology`.

        :return: :class:`NetworkTopology` with all cells registered.
        :raises TEIVError: If the TEIV service is unreachable.
        """
        _log.info("TEIV load_topology  url=%s%s", self._base, self._CELLS_PATH)
        try:
            resp = self._session.get(f"{self._base}{self._CELLS_PATH}", timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise TEIVError(f"TEIV load_topology failed: {exc}") from exc

        topo = NetworkTopology()
        for cell in resp.json().get("cells", []):
            topo.add(self._cell_to_node_info(cell))
        _log.info("TEIV topology loaded  cells=%d", len(topo.cells()))
        return topo

    def refresh_node(self, topology: NetworkTopology, cell_id: str) -> None:
        """Refresh a single node's state from TEIV.

        Call this from the O1 VES ``cellStatusChange`` handler to keep
        :class:`NetworkTopology` consistent without a full reload.

        :param topology: The :class:`NetworkTopology` instance to update.
        :param cell_id: Cell to refresh.
        :raises TEIVError: If the TEIV service is unreachable.
        """
        _log.debug("TEIV refresh_node  cell=%s", cell_id)
        try:
            resp = self._session.get(f"{self._base}{self._CELLS_PATH}/{cell_id}", timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise TEIVError(f"TEIV refresh_node({cell_id!r}) failed: {exc}") from exc

        node = self._cell_to_node_info(resp.json())
        topology.add(node)

    # --- Mapping helpers ----------------------------------------------------

    @staticmethod
    def _cell_to_node_info(cell: dict[str, Any]) -> NodeInfo:
        """Map a TEIV cell JSON object to a :class:`NodeInfo`.

        :param cell: TEIV cell response object.
        :return: :class:`NodeInfo`.
        """
        raw_type = cell.get("nodeType", "gnb").lower()
        try:
            node_type = NodeType(raw_type)
        except ValueError:
            node_type = NodeType.GNB

        return NodeInfo(
            cell_id=cell["cellId"],
            gnb_id=cell.get("gnbId", ""),
            vendor_id=cell.get("vendor", "unknown").lower(),
            node_type=node_type,
            is_active=cell.get("active", True),
        )


class TEIVError(RuntimeError):
    """Raised when a TEIV operation fails."""
