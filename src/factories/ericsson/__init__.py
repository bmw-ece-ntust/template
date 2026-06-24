"""Ericsson platform factory — proprietary RAN telemetry → 3GPP ``KpiReport``.

Selected via ``RAPP_PLATFORM=ericsson``.  This is a concrete
:class:`~factories.RAppPlatformFactory` for deployments that read telemetry
directly from an Ericsson management plane, whose PM counters use proprietary
``pm*`` names rather than the 3GPP TS 28.552 names the rApp core expects.

The Adapter pattern lives **inside** this factory's
:class:`EricssonKpiAnalyzer`: it translates Ericsson proprietary counter names
to spec-traceable :class:`~models.parameters.ThreeGPPKpi` via
:data:`ERICSSON_PARAM_MAP`, so the rApp core never sees proprietary names.
Standard O-RAN deployments (``RAPP_PLATFORM=osc``) need no such translation
because ICS delivers data already in 3GPP names.

The proprietary-name to 3GPP-name mapping below is illustrative and must be
validated against the Ericsson PM Counter reference for the deployed RAN
software level before production use.

References
    Abstract Factory: https://refactoring.guru/design-patterns/abstract-factory
    Adapter:          https://refactoring.guru/design-patterns/adapter
"""

from __future__ import annotations

import logging
from enum import Enum

import requests

from factories import KpiAnalyzer, RAppPlatformFactory, ScenarioRunner, TelemetryCollector
from models import KpiReport
from models.parameters import NodeType, ThreeGPPKpi, VendorParameterMap

_log = logging.getLogger(__name__)


class EricssonParam(str, Enum):
    """Ericsson proprietary PM counter names.

    Each member maps to a spec-traceable
    :class:`~models.parameters.ThreeGPPKpi` via :data:`ERICSSON_PARAM_MAP`.
    Values are the raw keys Ericsson telemetry returns; never reference them
    outside this factory.
    """

    PRB_USAGE_DL_PCT = "pmPrbUtilDl"  # → DRB.PrbUtilDL (TS 28.552 §5.1.1.12.1)
    PRB_USAGE_UL_PCT = "pmPrbUtilUl"  # → DRB.PrbUtilUL (TS 28.552 §5.1.1.12.2)
    RRC_CONN_AVG = "pmRrcConnLevAvg"  # → RRC.ConnMean (TS 28.552 §5.1.1.1.1)
    THP_DL_KBPS = "pmPdcpVolDlDrbKbps"  # → DRB.UEThpDL (TS 28.552 §5.1.1.10.1)
    THP_UL_KBPS = "pmPdcpVolUlDrbKbps"  # → DRB.UEThpUL (TS 28.552 §5.1.1.10.2)
    RSRP_DBM = "pmRadioRsrpAvg"  # → RSRP (TS 36.214 §5.1.1)
    SINR_DB = "pmRadioSinrAvg"  # → SINR (TS 36.214 §5.1.4)


#: Ericsson proprietary → 3GPP KPI translation table (Adapter pattern).
ERICSSON_PARAM_MAP = VendorParameterMap(
    {
        EricssonParam.PRB_USAGE_DL_PCT.value: ThreeGPPKpi.DRB_PRB_UTIL_DL,
        EricssonParam.PRB_USAGE_UL_PCT.value: ThreeGPPKpi.DRB_PRB_UTIL_UL,
        EricssonParam.RRC_CONN_AVG.value: ThreeGPPKpi.RRC_CONN_MEAN,
        EricssonParam.THP_DL_KBPS.value: ThreeGPPKpi.DRB_UE_THP_DL,
        EricssonParam.THP_UL_KBPS.value: ThreeGPPKpi.DRB_UE_THP_UL,
        EricssonParam.RSRP_DBM.value: ThreeGPPKpi.RSRP,
        EricssonParam.SINR_DB.value: ThreeGPPKpi.SINR,
    }
)

#: PM-counter REST path on the Ericsson management plane.  Placeholder — set to
#: the PM endpoint of the deployed ENM / OSS-RC instance.
_PM_PATH = "/pm/v1/cells/{cell_id}/counters"


class EricssonScenarioRunner(ScenarioRunner):
    """Connects to / disconnects from the Ericsson management plane.

    A logging no-op by default so the rApp boots against any environment;
    replace with real ENM session setup (authentication, subscription) for a
    production deployment.
    """

    def start(self) -> None:
        """Open the Ericsson management session (no-op stub)."""
        _log.info("EricssonScenarioRunner: started (no-op stub)")

    def stop(self) -> None:
        """Close the Ericsson management session (no-op stub)."""
        _log.info("EricssonScenarioRunner: stopped (no-op stub)")


class EricssonTelemetryCollector(TelemetryCollector):
    """Polls raw Ericsson proprietary PM counters from the management plane.

    :param ems_base_url: Base URL of the Ericsson ENM / OSS-RC PM API.
    :param cell_id: Cell whose counters are collected.
    """

    def __init__(self, ems_base_url: str, cell_id: str) -> None:
        self._base = ems_base_url.rstrip("/")
        self._cell_id = cell_id
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    def collect(self) -> dict[str, float]:
        """Fetch the latest proprietary PM counters for the cell.

        :return: ``{EricssonParam.value: float}`` raw proprietary counters.
        :raises RuntimeError: If the management-plane request fails.
        """
        url = self._base + _PM_PATH.format(cell_id=self._cell_id)
        _log.debug("Ericsson PM poll  %s", url)
        try:
            resp = self._session.get(url, timeout=10)
            resp.raise_for_status()
            return {k: float(v) for k, v in resp.json().items() if isinstance(v, (int, float))}
        except requests.RequestException as exc:
            raise RuntimeError(f"Ericsson PM poll failed for {self._cell_id!r}: {exc}") from exc


class EricssonKpiAnalyzer(KpiAnalyzer):
    """Adapts raw Ericsson proprietary counters to a standard ``KpiReport``.

    Applies :data:`ERICSSON_PARAM_MAP` (the Adapter translation table) and
    delegates field assembly to :meth:`~models.KpiReport.from_3gpp`, so the
    proprietary-to-3GPP mapping is the single auditable source of truth.

    :param cell_id: NR Cell Global ID annotated in the produced report.
    :param gnb_id: Parent gNB identifier.
    """

    def __init__(self, cell_id: str, gnb_id: str = "") -> None:
        self._cell_id = cell_id
        self._gnb_id = gnb_id

    def analyze(self, raw: dict[str, float]) -> KpiReport:
        """Translate proprietary counters and build a :class:`~models.KpiReport`.

        :param raw: ``{EricssonParam.value: float}`` from the collector.
            Unmapped keys are ignored.
        :return: Vendor-agnostic :class:`~models.KpiReport`.
        """
        standard = ERICSSON_PARAM_MAP.raw_to_standard(raw)
        return KpiReport.from_3gpp(
            self._cell_id, standard, gnb_id=self._gnb_id, node_type=NodeType.GNB
        )


class EricssonPlatformFactory(RAppPlatformFactory):
    """Abstract Factory for Ericsson management-plane deployments.

    :param ems_base_url: Ericsson ENM / OSS-RC PM API base URL.
    :param cell_id: Primary cell ID for collection and analysis.
    :param gnb_id: Parent gNB identifier for produced reports.

    :Example:

        >>> factory = EricssonPlatformFactory("http://enm:8080", "cell-er-0")
        >>> analyzer = factory.create_kpi_analyzer()
        >>> analyzer.analyze({"pmPrbUtilDl": 0.42}).prb_util_dl
        0.42
    """

    def __init__(self, ems_base_url: str, cell_id: str, gnb_id: str = "") -> None:
        self._ems_base_url = ems_base_url
        self._cell_id = cell_id
        self._gnb_id = gnb_id

    def create_scenario_runner(self) -> EricssonScenarioRunner:
        """Create an :class:`EricssonScenarioRunner`.

        :return: :class:`EricssonScenarioRunner`.
        """
        return EricssonScenarioRunner()

    def create_telemetry_collector(self) -> EricssonTelemetryCollector:
        """Create an :class:`EricssonTelemetryCollector` for this factory's cell.

        :return: :class:`EricssonTelemetryCollector`.
        """
        return EricssonTelemetryCollector(self._ems_base_url, self._cell_id)

    def create_kpi_analyzer(self) -> EricssonKpiAnalyzer:
        """Create an :class:`EricssonKpiAnalyzer` for this factory's cell.

        :return: :class:`EricssonKpiAnalyzer`.
        """
        return EricssonKpiAnalyzer(self._cell_id, self._gnb_id)
