"""Vendor adapter pattern — convert proprietary gNB telemetry to 3GPP KPIs.

Reference: https://refactoring.guru/design-patterns/adapter
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import KpiReport


class VendorTelemetryClient(ABC):
    """Abstract interface for a vendor-specific telemetry client."""

    @abstractmethod
    def get_metric(self, metric_name: str) -> float:
        """Retrieve a raw vendor metric by name.

        :param metric_name: Vendor-specific metric key.
        :return: Raw metric value as float.
        """


class GnbTelemetryAdapter:
    """Adapts vendor-specific gNB telemetry to standard 3GPP KPIs.

    :param vendor_client: An implementation of :class:`VendorTelemetryClient`.

    :Example:

        >>> adapter = GnbTelemetryAdapter(my_vendor_client)
        >>> report = adapter.get_kpi_report("cell-001")
    """

    def __init__(self, vendor_client: VendorTelemetryClient) -> None:
        self._client = vendor_client

    def get_prb_util_dl(self) -> float:
        """Return DL PRB utilization normalized to ``[0.0, 1.0]``.

        Maps ``dl_prb_usage_pct`` →
        `DRB.PrbUtilDL <https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/>`_
        (TS 28.552 §5.1.1.12.1).

        :return: DRB.PrbUtilDL as a float in ``[0.0, 1.0]``.
        """
        raw = self._client.get_metric("dl_prb_usage_pct")
        return float(raw) / 100.0

    def get_prb_util_ul(self) -> float:
        """Return UL PRB utilization normalized to ``[0.0, 1.0]``.

        Maps ``ul_prb_usage_pct`` →
        `DRB.PrbUtilUL <https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/>`_
        (TS 28.552 §5.1.1.12.2).

        :return: DRB.PrbUtilUL as a float in ``[0.0, 1.0]``.
        """
        raw = self._client.get_metric("ul_prb_usage_pct")
        return float(raw) / 100.0

    def get_kpi_report(self, cell_id: str) -> KpiReport:
        """Build a complete :class:`core.models.KpiReport` for a cell.

        :param cell_id: NR Cell Global ID.
        :return: Standardized :class:`~core.models.KpiReport`.
        :raises ValueError: If the vendor client returns unexpected data types.
        """
        return KpiReport(
            cell_id=cell_id,
            prb_util_dl=self.get_prb_util_dl(),
            prb_util_ul=self.get_prb_util_ul(),
            active_ue_count=int(self._client.get_metric("active_ue_count")),
        )
