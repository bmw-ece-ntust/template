"""Vendor adapter pattern — convert proprietary gNB / AP telemetry to 3GPP KPIs.

The Adapter pattern is used here to normalize vendor-specific metric names
into the standard :class:`~core.models.parameters.ThreeGPPKpi` identifiers,
so rApp core logic never sees proprietary parameter names.

For WiFi APs (e.g. Aruba), subclass :class:`VendorTelemetryClient` and map
IEEE 802.11 metrics (RSSI, channel utilization, association count) to the
closest 3GPP equivalents in :attr:`PARAM_MAP`.  See the BMW Lab Aruba
project for a reference implementation.

Reference: https://refactoring.guru/design-patterns/adapter
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import KpiReport
from core.models.parameters import NodeType, ThreeGPPKpi


class VendorTelemetryClient(ABC):
    """Abstract interface for a vendor-specific telemetry client.

    Subclass this for each vendor.  Declare a ``PARAM_MAP`` class variable
    to make the proprietary → 3GPP translation explicit and auditable::

        class EricsonClient(VendorTelemetryClient):
            PARAM_MAP: ClassVar[dict[str, ThreeGPPKpi]] = {
                "dl_prb_usage_pct": ThreeGPPKpi.DRB_PRB_UTIL_DL,
                "ul_prb_usage_pct": ThreeGPPKpi.DRB_PRB_UTIL_UL,
                "active_ue_count":  ThreeGPPKpi.RRC_CONN_MEAN,
                "dl_thr_kbps":      ThreeGPPKpi.DRB_UE_THP_DL,
                "ul_thr_kbps":      ThreeGPPKpi.DRB_UE_THP_UL,
            }
    """

    @abstractmethod
    def get_metric(self, metric_name: str) -> float:
        """Retrieve a raw vendor metric by its proprietary name.

        :param metric_name: Vendor-specific metric key.
        :return: Raw metric value as float.
        """


class GnbTelemetryAdapter:
    """Adapts vendor-specific gNB / AP telemetry to standard 3GPP KPIs.

    Uses :class:`~core.models.parameters.ThreeGPPKpi` enum values for all
    parameter lookups, eliminating raw string literals in the adapter logic.

    :param vendor_client: An implementation of :class:`VendorTelemetryClient`.
    :param node_type: :class:`~core.models.parameters.NodeType` of the managed node.

    :Example:

        >>> adapter = GnbTelemetryAdapter(my_vendor_client)
        >>> report = adapter.get_kpi_report("cell-001", gnb_id="gnb-1")
    """

    def __init__(
        self,
        vendor_client: VendorTelemetryClient,
        node_type: NodeType = NodeType.GNB,
    ) -> None:
        self._client = vendor_client
        self._node_type = node_type

    def get_prb_util_dl(self) -> float:
        """Return DL PRB utilization normalized to ``[0.0, 1.0]``.

        Maps vendor ``dl_prb_usage_pct`` →
        `DRB.PrbUtilDL
        <https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/28552-i50.zip>`_
        (TS 28.552 §5.1.1.12.1, Table 5.1.1.12.1-1, p.47).

        :return: DRB.PrbUtilDL as a ratio in ``[0.0, 1.0]``.
        """
        raw = self._client.get_metric("dl_prb_usage_pct")
        return float(raw) / 100.0

    def get_prb_util_ul(self) -> float:
        """Return UL PRB utilization normalized to ``[0.0, 1.0]``.

        Maps vendor ``ul_prb_usage_pct`` →
        `DRB.PrbUtilUL
        <https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/28552-i50.zip>`_
        (TS 28.552 §5.1.1.12.2, Table 5.1.1.12.2-1, p.48).

        :return: DRB.PrbUtilUL as a ratio in ``[0.0, 1.0]``.
        """
        raw = self._client.get_metric("ul_prb_usage_pct")
        return float(raw) / 100.0

    def get_kpi_report(self, cell_id: str, gnb_id: str = "") -> KpiReport:
        """Build a complete :class:`~core.models.KpiReport` for a cell.

        :param cell_id: NR Cell Global ID.
        :param gnb_id: Parent gNB identifier (optional).
        :return: Standardised :class:`~core.models.KpiReport`.
        :raises ValueError: If the vendor client returns unexpected data types.
        """

        def _safe(metric: str, default: float = 0.0) -> float:
            try:
                return float(self._client.get_metric(metric))
            except Exception:
                return default

        return KpiReport(
            cell_id=cell_id,
            gnb_id=gnb_id,
            node_type=self._node_type,
            prb_util_dl=self.get_prb_util_dl(),
            prb_util_ul=self.get_prb_util_ul(),
            active_ue_count=int(_safe("active_ue_count")),
            dl_throughput_kbps=_safe("dl_thr_kbps"),
            ul_throughput_kbps=_safe("ul_thr_kbps"),
            rsrp_dbm=_safe("rsrp_dbm") or None,
            rsrq_db=_safe("rsrq_db") or None,
            sinr_db=_safe("sinr_db") or None,
        )
