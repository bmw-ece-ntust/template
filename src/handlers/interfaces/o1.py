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

Used by controllers to read and patch cell YANG configuration over O1.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

import requests

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Vendor-independent port contract (ABC)
# ---------------------------------------------------------------------------


class O1Client(ABC):
    """Abstract O1 client — vendor-independent managed-object operations.

    Concrete subclasses map each semantic method to the appropriate transport:
    SDNC REST relay (:class:`O1SdncAdapter`), or direct NETCONF session via
    ``ncclient`` for physical testbed deployments.

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


# ---------------------------------------------------------------------------
# SDNC-relay implementation  (O-RAN SC / Non-RT RIC lab)
# ---------------------------------------------------------------------------


class O1SdncAdapter(O1Client):
    """Adapts O1 managed-object operations to the SDNC REST API.

    This is the canonical integration path used by O-RAN SC rApps:

    .. code-block:: none

        rApp → O1SdncAdapter → SDNC REST → NETCONF → gNB

    The ``set_admission_control`` and ``restore_admission_control`` helpers
    demonstrate the multi-vendor mapping: the semantic operation is fixed, but
    the YANG key can be overridden per vendor by subclassing.

    :param sdnc_base_url: Base URL of the SDNC northbound REST API
        (e.g. ``http://sdnc.nonrtric.svc.cluster.local:8282``).
    :param auth: ``(username, password)`` for HTTP Basic auth.
                 Pass ``None`` for unauthenticated lab setups.

    :Example:

        >>> adapter = O1SdncAdapter(
        ...     sdnc_base_url="http://sdnc.nonrtric.svc.cluster.local:8282",
        ...     auth=("admin", "Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U"),
        ... )
        >>> cfg = adapter.get_cell_config("o-du-1111/cell-0")
        >>> adapter.set_admission_control("o-du-1111/cell-0", max_ue_count=32)

    .. note::

        YANG paths follow O-RAN WG5 O1 Interface Specification (O-RAN.WG5.O1)
        with attribute keys from the ``o-ran-sc-du-hello-world`` YANG model as
        shipped with O-RAN SC SDNC integration tests.  Subclass and override
        :attr:`_YANG_MAX_UES` to adapt to a different vendor model.
    """

    _TOPOLOGY_BASE = "/rests/data/network-topology:network-topology/topology=o-ran-sc-topology"

    #: YANG leaf name for the UE admission limit.
    #: Override in a vendor-specific subclass when the vendor uses a
    #: different YANG module for this parameter.
    _YANG_MAX_UES: str = "o-ran-sc-du-hello-world:max-ues"

    def __init__(
        self,
        sdnc_base_url: str,
        auth: tuple[str, str] | None = None,
    ) -> None:
        self._base = sdnc_base_url.rstrip("/")
        self._session = requests.Session()
        if auth:
            self._session.auth = auth
        self._session.headers.update(
            {
                "Content-Type": "application/yang-data+json",
                "Accept": "application/yang-data+json",
            }
        )

    # --- O1Client implementation --------------------------------------------

    def get_cell_config(self, cell_id: str) -> dict[str, Any]:
        """Return YANG config for *cell_id* via SDNC REST (HTTP GET).

        :param cell_id: O-DU node-ID and cell index, e.g. ``o-du-1111/cell-0``.
        :return: Parsed JSON body as a flat dictionary.
        :raises O1Error: On HTTP error or unreachable SDNC.
        """
        url = f"{self._base}{self._TOPOLOGY_BASE}/node={cell_id}"
        _log.debug("O1 GET %s", url)
        try:
            resp = self._session.get(url, timeout=10)
            resp.raise_for_status()
            config: dict[str, Any] = resp.json()
            return config
        except requests.RequestException as exc:
            raise O1Error(f"get_cell_config({cell_id!r}) failed: {exc}") from exc

    def set_cell_config(self, cell_id: str, config: dict[str, Any]) -> None:
        """Apply a config patch to *cell_id* via SDNC REST (HTTP PATCH).

        :param cell_id: O-DU node-ID and cell index.
        :param config: Partial YANG attributes to update.
        :raises O1Error: On HTTP error or rejected configuration.
        """
        url = f"{self._base}{self._TOPOLOGY_BASE}/node={cell_id}"
        _log.debug("O1 PATCH %s  body=%s", url, config)
        try:
            resp = self._session.patch(url, data=json.dumps(config), timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise O1Error(f"set_cell_config({cell_id!r}) failed: {exc}") from exc

    # --- Semantic helpers (vendor-mapping layer) ----------------------------

    def set_admission_control(self, cell_id: str, max_ue_count: int) -> None:
        """Limit UE admission on a cell via the O1 YANG model.

        Maps the semantic operation to the :attr:`_YANG_MAX_UES` leaf.
        Subclass and override :attr:`_YANG_MAX_UES` to target a different
        vendor YANG module without changing the call site.

        :param cell_id: NR Cell Global ID.
        :param max_ue_count: Maximum admitted UEs (``0`` = unlimited / restore).
        :raises O1Error: If the managed element rejects the configuration.
        """
        _log.info("O1 set_admission_control  cell=%s  max_ue=%d", cell_id, max_ue_count)
        self.set_cell_config(cell_id, {self._YANG_MAX_UES: max_ue_count})

    def restore_admission_control(self, cell_id: str) -> None:
        """Restore default (unlimited) UE admission on a cell via O1.

        Convenience wrapper around :meth:`set_admission_control` with
        ``max_ue_count=0``.

        :param cell_id: NR Cell Global ID.
        :raises O1Error: If the managed element rejects the configuration.
        """
        _log.info("O1 restore_admission_control  cell=%s", cell_id)
        self.set_admission_control(cell_id, max_ue_count=0)


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class O1Error(RuntimeError):
    """Raised when an O1 interface operation fails."""
