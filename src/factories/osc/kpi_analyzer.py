"""3GPP-named ICS payload to :class:`~models.KpiReport` analyzer (no vendor translation)."""

from __future__ import annotations

from factories import KpiAnalyzer
from models import KpiReport
from models.parameters import ThreeGPPKpi


class OscKpiAnalyzer(KpiAnalyzer):
    """Translates raw ICS PM counter payloads into standardized KPI reports.

    ICS delivers performance-measurement data using 3GPP counter names
    (e.g. ``DRB.PrbUtilDL``, ``RRC.ConnMean``).  This analyzer maps those
    names directly to :class:`~models.KpiReport` fields without any
    vendor-specific translation — the O-RAN standard guarantees the names.

    :param cell_id: NR Cell Global ID annotated in the produced report.

    :Example:

        >>> analyzer = OscKpiAnalyzer("o-du-1111/cell-0")
        >>> report = analyzer.analyze({"DRB.PrbUtilDL": 0.72, "RRC.ConnMean": 14.0})
    """

    def __init__(self, cell_id: str) -> None:
        self._cell_id = cell_id

    def analyze(self, raw: dict[str, float]) -> KpiReport:
        """Convert ICS raw PM counters to a :class:`~models.KpiReport`.

        Expected keys in *raw* (3GPP TS 28.552):

        - ``DRB.PrbUtilDL`` — DL PRB utilization ratio (Section 5.1.1.12.1)
        - ``DRB.PrbUtilUL`` — UL PRB utilization ratio (Section 5.1.1.12.2)
        - ``RRC.ConnMean``  — Mean number of active UE connections

        Missing keys default to ``0`` / ``0.0``.

        :param raw: Raw PM counter dict from
            :class:`~factories.osc.OscIcsTelemetryCollector`.
        :return: Standardized :class:`~models.KpiReport`.
        """
        return KpiReport(
            cell_id=self._cell_id,
            prb_util_dl=raw.get(ThreeGPPKpi.DRB_PRB_UTIL_DL.value, 0.0),
            prb_util_ul=raw.get(ThreeGPPKpi.DRB_PRB_UTIL_UL.value, 0.0),
            active_ue_count=int(raw.get(ThreeGPPKpi.RRC_CONN_MEAN.value, 0)),
            dl_throughput_kbps=raw.get(ThreeGPPKpi.DRB_UE_THP_DL.value, 0.0),
            ul_throughput_kbps=raw.get(ThreeGPPKpi.DRB_UE_THP_UL.value, 0.0),
        )
