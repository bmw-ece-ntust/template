"""Tests for the MockPlatformFactory (Abstract Factory pattern)."""

from __future__ import annotations

from factories.mock import MockPlatformFactory
from models import KpiReport
from models.parameters import ThreeGPPKpi


def test_factory_creates_compatible_components() -> None:
    factory = MockPlatformFactory()
    runner = factory.create_scenario_runner()
    collector = factory.create_telemetry_collector()
    analyzer = factory.create_kpi_analyzer()
    # Runner is a no-op; must not raise.
    runner.start()
    runner.stop()
    raw = collector.collect()
    assert raw[ThreeGPPKpi.DRB_PRB_UTIL_DL.value] == 0.45
    assert analyzer.analyze(raw).cell_id == "mock-cell-0"


def test_custom_fixture_flows_through_to_report() -> None:
    fixture = {
        ThreeGPPKpi.DRB_PRB_UTIL_DL.value: 0.77,
        ThreeGPPKpi.RRC_CONN_MEAN.value: 5.0,
    }
    factory = MockPlatformFactory(fixture=fixture, cell_id="c-9", gnb_id="g-9")
    raw = factory.create_telemetry_collector().collect()
    report = factory.create_kpi_analyzer().analyze(raw)
    assert isinstance(report, KpiReport)
    assert report.cell_id == "c-9"
    assert report.prb_util_dl == 0.77
    assert report.active_ue_count == 5
