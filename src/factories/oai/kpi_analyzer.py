"""Adapter — raw OAI/FlexRIC KPM measurements to a standard ``KpiReport``."""

from __future__ import annotations

from factories.kpi_analyzer import KpiAnalyzer
from factories.oai.params import OAI_PARAM_MAP
from models import KpiReport
from models.parameters import NodeType


class OaiKpiAnalyzer(KpiAnalyzer):
    """Adapts raw OAI/FlexRIC KPM measurements to a standard ``KpiReport``.

    Applies :data:`~factories.oai.OAI_PARAM_MAP` (the Adapter translation
    table) and delegates field assembly to
    :meth:`~models.KpiReport.from_3gpp`, so the OAI-to-3GPP mapping is the
    single auditable source of truth.  Volume counters without a 3GPP field
    equivalent (e.g. ``DRB.PdcpSduVolumeDL``) are dropped.

    :param cell_id: NR Cell Global ID annotated in the produced report.
    :param gnb_id: Parent gNB identifier.
    """

    def __init__(self, cell_id: str, gnb_id: str = "") -> None:
        self._cell_id = cell_id
        self._gnb_id = gnb_id

    def analyze(self, raw: dict[str, float]) -> KpiReport:
        """Translate OAI measurements and build a :class:`~models.KpiReport`.

        :param raw: ``{OaiParam.value: float}`` from the collector.
            Unmapped keys are ignored.
        :return: Vendor-agnostic :class:`~models.KpiReport`.
        """
        standard = OAI_PARAM_MAP.raw_to_standard(raw)
        return KpiReport.from_3gpp(
            self._cell_id, standard, gnb_id=self._gnb_id, node_type=NodeType.GNB
        )
