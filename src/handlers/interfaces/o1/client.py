"""Abstract O1 client — vendor-independent managed-object operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class O1Client(ABC):
    """Abstract O1 client — vendor-independent managed-object operations.

    Concrete subclasses map each semantic method to the appropriate transport:
    SDNC REST relay (:class:`~handlers.interfaces.o1.O1SdncAdapter`), or direct
    NETCONF session via ``ncclient`` for physical testbed deployments.
    """

    @abstractmethod
    def get_cell_config(self, cell_id: str) -> dict[str, Any]:
        """Retrieve the current YANG configuration for a cell.

        :param cell_id: NR Cell Global ID (e.g. ``o-du-1111/cell-0``).
        :return: Flat mapping of YANG attribute-name → value.
        :raises O1Error: If the managed element is unreachable.
        """

    @abstractmethod
    def set_cell_config(self, cell_id: str, config: dict[str, Any]) -> None:
        """Apply a partial YANG configuration patch to a cell.

        :param cell_id: NR Cell Global ID.
        :param config: Partial YANG attribute-name → new value mapping.
        :raises O1Error: If the request is rejected by the managed element.
        """
