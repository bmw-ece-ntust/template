"""Mock platform factory — in-memory implementations for unit tests and demos.

Use this factory when ``RAPP_PLATFORM=mock`` (the default).  No network
connections, no simulator, no Non-RT RIC required.

Run as the default platform::

    RAPP_PLATFORM=mock python src/main.py

Or drive it directly in tests::

    factory = MockPlatformFactory(
        fixture={
            "DRB.PrbUtilDL": 0.45,
            "DRB.PrbUtilUL": 0.30,
            "RRC.ConnMean": 12.0,
        }
    )
    collector = factory.create_telemetry_collector()
    assert collector.collect()["DRB.PrbUtilDL"] == 0.45
"""

from __future__ import annotations

import logging

from factories import KpiAnalyzer, RAppPlatformFactory, ScenarioRunner, TelemetryCollector
from models import KpiReport
from models.parameters import ThreeGPPKpi

_log = logging.getLogger(__name__)

_DEFAULT_FIXTURE: dict[str, float] = {
    ThreeGPPKpi.DRB_PRB_UTIL_DL.value: 0.45,
    ThreeGPPKpi.DRB_PRB_UTIL_UL.value: 0.30,
    ThreeGPPKpi.RRC_CONN_MEAN.value: 12.0,
    ThreeGPPKpi.DRB_UE_THP_DL.value: 25_000.0,
    ThreeGPPKpi.DRB_UE_THP_UL.value: 10_000.0,
}


class MockScenarioRunner(ScenarioRunner):
    """No-op scenario runner — logs start/stop without side effects."""

    def start(self) -> None:
        """Log start; no network or simulator interaction.

        :return: None
        """
        _log.info("MockScenarioRunner: started (no-op)")

    def stop(self) -> None:
        """Log stop; no network or simulator interaction.

        :return: None
        """
        _log.info("MockScenarioRunner: stopped (no-op)")


class MockTelemetryCollector(TelemetryCollector):
    """Returns a configurable fixed KPI fixture.

    :param fixture: ``{3GPP counter name: value}`` dict.  Defaults to
        :data:`_DEFAULT_FIXTURE` when not provided.
    """

    def __init__(self, fixture: dict[str, float] | None = None) -> None:
        self._fixture = fixture or _DEFAULT_FIXTURE.copy()

    def collect(self) -> dict[str, float]:
        """Return the configured fixture dict.

        :return: ``{ThreeGPPKpi.value: float}`` fixture.
        """
        return dict(self._fixture)


class MockKpiAnalyzer(KpiAnalyzer):
    """Maps fixture dict directly to a :class:`~models.KpiReport`.

    :param cell_id: Cell ID to embed in the produced report.
    :param gnb_id: gNB ID to embed in the produced report.
    """

    def __init__(self, cell_id: str = "mock-cell-0", gnb_id: str = "mock-gnb-0") -> None:
        self._cell_id = cell_id
        self._gnb_id = gnb_id

    def analyze(self, raw: dict[str, float]) -> KpiReport:
        """Build a :class:`~models.KpiReport` from the fixture dict.

        :param raw: Raw metric dict from :class:`MockTelemetryCollector`.
        :return: :class:`~models.KpiReport`.
        """
        return KpiReport(
            cell_id=self._cell_id,
            gnb_id=self._gnb_id,
            prb_util_dl=raw.get(ThreeGPPKpi.DRB_PRB_UTIL_DL.value, 0.0),
            prb_util_ul=raw.get(ThreeGPPKpi.DRB_PRB_UTIL_UL.value, 0.0),
            active_ue_count=int(raw.get(ThreeGPPKpi.RRC_CONN_MEAN.value, 0)),
            dl_throughput_kbps=raw.get(ThreeGPPKpi.DRB_UE_THP_DL.value, 0.0),
            ul_throughput_kbps=raw.get(ThreeGPPKpi.DRB_UE_THP_UL.value, 0.0),
        )


class MockPlatformFactory(RAppPlatformFactory):
    """Factory for in-memory mock components (no external dependencies).

    :param fixture: Optional KPI fixture for :class:`MockTelemetryCollector`.
    :param cell_id: Cell ID for :class:`MockKpiAnalyzer`.
    :param gnb_id: gNB ID for :class:`MockKpiAnalyzer`.
    """

    def __init__(
        self,
        fixture: dict[str, float] | None = None,
        cell_id: str = "mock-cell-0",
        gnb_id: str = "mock-gnb-0",
    ) -> None:
        self._fixture = fixture
        self._cell_id = cell_id
        self._gnb_id = gnb_id

    def create_scenario_runner(self) -> MockScenarioRunner:
        """Create a no-op :class:`MockScenarioRunner`.

        :return: :class:`MockScenarioRunner`.
        """
        return MockScenarioRunner()

    def create_telemetry_collector(self) -> MockTelemetryCollector:
        """Create a :class:`MockTelemetryCollector` with the configured fixture.

        :return: :class:`MockTelemetryCollector`.
        """
        return MockTelemetryCollector(self._fixture)

    def create_kpi_analyzer(self) -> MockKpiAnalyzer:
        """Create a :class:`MockKpiAnalyzer`.

        :return: :class:`MockKpiAnalyzer`.
        """
        return MockKpiAnalyzer(self._cell_id, self._gnb_id)
