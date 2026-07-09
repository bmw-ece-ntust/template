"""Adapter — raw OCUDU metrics to a standard ``KpiReport`` (names and units)."""

from __future__ import annotations

from factories.kpi_analyzer import KpiAnalyzer
from factories.ocudu.params import OCUDU_PARAM_MAP, OcuduParam
from models import KpiReport
from models.parameters import NodeType


class OcuduKpiAnalyzer(KpiAnalyzer):
    """Adapts raw OCUDU metrics to a standard ``KpiReport``.

    Demonstrates that an Adapter owns **both** translation directions the
    3GPP contract needs: naming (:data:`~factories.ocudu.OCUDU_PARAM_MAP`)
    and units (OCUDU bitrates arrive in bit/s while ``DRB.UEThp*`` is
    defined in kbps, TS 28.552 §5.1.1.10.1).  Field assembly is delegated
    to :meth:`~models.KpiReport.from_3gpp`.

    :param cell_id: NR Cell Global ID annotated in the produced report.
    :param gnb_id: Parent gNB identifier.
    """

    #: Metric keys reported in bit/s that must be rescaled to kbps.
    _BPS_KEYS = frozenset(
        {OcuduParam.DL_BITRATE_BPS.value, OcuduParam.UL_BITRATE_BPS.value}
    )

    def __init__(self, cell_id: str, gnb_id: str = "") -> None:
        self._cell_id = cell_id
        self._gnb_id = gnb_id

    def analyze(self, raw: dict[str, float]) -> KpiReport:
        """Rescale units, translate names, and build a :class:`~models.KpiReport`.

        :param raw: ``{OcuduParam.value: float}`` from the collector.
            Unmapped keys are ignored.
        :return: Vendor-agnostic :class:`~models.KpiReport`.
        """
        scaled = {
            key: value / 1000.0 if key in self._BPS_KEYS else value
            for key, value in raw.items()
        }
        standard = OCUDU_PARAM_MAP.raw_to_standard(scaled)
        return KpiReport.from_3gpp(
            self._cell_id, standard, gnb_id=self._gnb_id, node_type=NodeType.GNB
        )
