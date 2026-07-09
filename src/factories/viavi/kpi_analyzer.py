"""Adapter — raw VIAVI RIC Test KPIs to a standard ``KpiReport``."""

from __future__ import annotations

from factories.kpi_analyzer import KpiAnalyzer
from factories.viavi.params import VIAVI_PARAM_MAP
from models import KpiReport
from models.parameters import NodeType


class ViaviKpiAnalyzer(KpiAnalyzer):
    """Adapts raw VIAVI RIC Test KPIs to a standard ``KpiReport``.

    Applies :data:`~factories.viavi.VIAVI_PARAM_MAP` (the Adapter
    translation table) and delegates field assembly to
    :meth:`~models.KpiReport.from_3gpp`, so the VIAVI-to-3GPP mapping is
    the single auditable source of truth.  Proprietary keys without a 3GPP
    equivalent (e.g. ``Viavi.QoS.Score``) are dropped.

    :param cell_id: NR Cell Global ID annotated in the produced report.
    :param gnb_id: Parent gNB identifier.
    """

    def __init__(self, cell_id: str, gnb_id: str = "") -> None:
        self._cell_id = cell_id
        self._gnb_id = gnb_id

    def analyze(self, raw: dict[str, float]) -> KpiReport:
        """Translate VIAVI KPIs and build a :class:`~models.KpiReport`.

        :param raw: ``{ViaviParam.value: float}`` from the collector.
            Unmapped keys are ignored.
        :return: Vendor-agnostic :class:`~models.KpiReport`.
        """
        standard = VIAVI_PARAM_MAP.raw_to_standard(raw)
        return KpiReport.from_3gpp(
            self._cell_id, standard, gnb_id=self._gnb_id, node_type=NodeType.GNB
        )
