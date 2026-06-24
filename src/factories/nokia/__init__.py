"""Nokia platform factory — proprietary RAN telemetry → 3GPP ``KpiReport``.

Selected via ``RAPP_PLATFORM=nokia``.  This is a concrete
:class:`~factories.RAppPlatformFactory` for deployments that read telemetry
directly from a Nokia management plane, whose AirScale PM counters use
proprietary ``NR_*`` names rather than the 3GPP TS 28.552 names the rApp core
expects.

The Adapter pattern lives **inside** this factory's :class:`NokiaKpiAnalyzer`:
it translates Nokia proprietary counter names to spec-traceable
:class:`~models.parameters.ThreeGPPKpi` via :data:`NOKIA_PARAM_MAP`, so the
rApp core never sees proprietary names.  Standard O-RAN deployments
(``RAPP_PLATFORM=osc``) need no such translation because ICS delivers data
already in 3GPP names.

The proprietary-name to 3GPP-name mapping below is illustrative and must be
validated against the Nokia PM Counter reference for the deployed RAN software
level before production use.

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


class NokiaParam(str, Enum):
    """Nokia proprietary PM counter names.

    Each member maps to a spec-traceable
    :class:`~models.parameters.ThreeGPPKpi` via :data:`NOKIA_PARAM_MAP`.
    """

    PRB_UTIL_DL = "NR_PrbUsedDlPct"  # → DRB.PrbUtilDL (TS 28.552 §5.1.1.12.1)
    PRB_UTIL_UL = "NR_PrbUsedUlPct"  # → DRB.PrbUtilUL (TS 28.552 §5.1.1.12.2)
    CONN_UE_AVG = "NR_RrcConnUeAvg"  # → RRC.ConnMean (TS 28.552 §5.1.1.1.1)
    THP_DL_KBPS = "NR_DlThpVolKbps"  # → DRB.UEThpDL (TS 28.552 §5.1.1.10.1)
    THP_UL_KBPS = "NR_UlThpVolKbps"  # → DRB.UEThpUL (TS 28.552 §5.1.1.10.2)
    RSRP_DBM = "NR_RsrpMeanDbm"  # → RSRP (TS 36.214 §5.1.1)
    RSRQ_DB = "NR_RsrqMeanDb"  # → RSRQ (TS 36.214 §5.1.2)


#: Nokia proprietary → 3GPP KPI translation table (Adapter pattern).
NOKIA_PARAM_MAP = VendorParameterMap(
    {
        NokiaParam.PRB_UTIL_DL.value: ThreeGPPKpi.DRB_PRB_UTIL_DL,
        NokiaParam.PRB_UTIL_UL.value: ThreeGPPKpi.DRB_PRB_UTIL_UL,
        NokiaParam.CONN_UE_AVG.value: ThreeGPPKpi.RRC_CONN_MEAN,
        NokiaParam.THP_DL_KBPS.value: ThreeGPPKpi.DRB_UE_THP_DL,
        NokiaParam.THP_UL_KBPS.value: ThreeGPPKpi.DRB_UE_THP_UL,
        NokiaParam.RSRP_DBM.value: ThreeGPPKpi.RSRP,
        NokiaParam.RSRQ_DB.value: ThreeGPPKpi.RSRQ,
    }
)

#: PM-counter REST path on the Nokia management plane.  Placeholder — set to the
#: PM endpoint of the deployed NetAct / MantaRay instance.
_PM_PATH = "/pm/v1/cells/{cell_id}/counters"


class NokiaScenarioRunner(ScenarioRunner):
    """Connects to / disconnects from the Nokia management plane.

    A logging no-op by default so the rApp boots against any environment;
    replace with real NetAct session setup for a production deployment.
    """

    def start(self) -> None:
        """Open the Nokia management session (no-op stub)."""
        _log.info("NokiaScenarioRunner: started (no-op stub)")

    def stop(self) -> None:
        """Close the Nokia management session (no-op stub)."""
        _log.info("NokiaScenarioRunner: stopped (no-op stub)")


class NokiaTelemetryCollector(TelemetryCollector):
    """Polls raw Nokia proprietary PM counters from the management plane.

    :param ems_base_url: Base URL of the Nokia NetAct / MantaRay PM API.
    :param cell_id: Cell whose counters are collected.
    """

    def __init__(self, ems_base_url: str, cell_id: str) -> None:
        self._base = ems_base_url.rstrip("/")
        self._cell_id = cell_id
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    def collect(self) -> dict[str, float]:
        """Fetch the latest proprietary PM counters for the cell.

        :return: ``{NokiaParam.value: float}`` raw proprietary counters.
        :raises RuntimeError: If the management-plane request fails.
        """
        url = self._base + _PM_PATH.format(cell_id=self._cell_id)
        _log.debug("Nokia PM poll  %s", url)
        try:
            resp = self._session.get(url, timeout=10)
            resp.raise_for_status()
            return {k: float(v) for k, v in resp.json().items() if isinstance(v, (int, float))}
        except requests.RequestException as exc:
            raise RuntimeError(f"Nokia PM poll failed for {self._cell_id!r}: {exc}") from exc


class NokiaKpiAnalyzer(KpiAnalyzer):
    """Adapts raw Nokia proprietary counters to a standard ``KpiReport``.

    Applies :data:`NOKIA_PARAM_MAP` (the Adapter translation table) and
    delegates field assembly to :meth:`~models.KpiReport.from_3gpp`.

    :param cell_id: NR Cell Global ID annotated in the produced report.
    :param gnb_id: Parent gNB identifier.
    """

    def __init__(self, cell_id: str, gnb_id: str = "") -> None:
        self._cell_id = cell_id
        self._gnb_id = gnb_id

    def analyze(self, raw: dict[str, float]) -> KpiReport:
        """Translate proprietary counters and build a :class:`~models.KpiReport`.

        :param raw: ``{NokiaParam.value: float}`` from the collector.
            Unmapped keys are ignored.
        :return: Vendor-agnostic :class:`~models.KpiReport`.
        """
        standard = NOKIA_PARAM_MAP.raw_to_standard(raw)
        return KpiReport.from_3gpp(
            self._cell_id, standard, gnb_id=self._gnb_id, node_type=NodeType.GNB
        )


class NokiaPlatformFactory(RAppPlatformFactory):
    """Abstract Factory for Nokia management-plane deployments.

    :param ems_base_url: Nokia NetAct / MantaRay PM API base URL.
    :param cell_id: Primary cell ID for collection and analysis.
    :param gnb_id: Parent gNB identifier for produced reports.

    :Example:

        >>> factory = NokiaPlatformFactory("http://netact:8080", "cell-nok-0")
        >>> analyzer = factory.create_kpi_analyzer()
        >>> analyzer.analyze({"NR_PrbUsedDlPct": 0.30}).prb_util_dl
        0.3
    """

    def __init__(self, ems_base_url: str, cell_id: str, gnb_id: str = "") -> None:
        self._ems_base_url = ems_base_url
        self._cell_id = cell_id
        self._gnb_id = gnb_id

    def create_scenario_runner(self) -> NokiaScenarioRunner:
        """Create a :class:`NokiaScenarioRunner`.

        :return: :class:`NokiaScenarioRunner`.
        """
        return NokiaScenarioRunner()

    def create_telemetry_collector(self) -> NokiaTelemetryCollector:
        """Create a :class:`NokiaTelemetryCollector` for this factory's cell.

        :return: :class:`NokiaTelemetryCollector`.
        """
        return NokiaTelemetryCollector(self._ems_base_url, self._cell_id)

    def create_kpi_analyzer(self) -> NokiaKpiAnalyzer:
        """Create a :class:`NokiaKpiAnalyzer` for this factory's cell.

        :return: :class:`NokiaKpiAnalyzer`.
        """
        return NokiaKpiAnalyzer(self._cell_id, self._gnb_id)
