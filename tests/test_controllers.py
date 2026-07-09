"""Tests for the controllers layer: KpiController loop and health payload."""

from __future__ import annotations

from conftest import FakeTelemetryCollector
from controllers.health import HealthService, get_health_payload
from controllers.kpi_controller import KpiController
from controllers.strategies import MlBasedStrategy, ThresholdBasedStrategy
from factories.osc import OscKpiAnalyzer
from models import PolicyDecision
from models.parameters import ThreeGPPKpi


def _controller(prb: float) -> KpiController:
    return KpiController(
        collector=FakeTelemetryCollector({ThreeGPPKpi.DRB_PRB_UTIL_DL.value: prb}),
        analyzer=OscKpiAnalyzer("cell-x"),
        strategy=ThresholdBasedStrategy(threshold_low=0.2),
    )


def test_kpi_controller_runs_one_cycle() -> None:
    # Low DL PRB → strategy should choose SLEEP.
    report, decision = _controller(0.05).evaluate_once()
    assert report.cell_id == "cell-x"
    assert decision is PolicyDecision.SLEEP


def test_set_strategy_swaps_algorithm_at_runtime() -> None:
    controller = _controller(0.05)
    assert controller.evaluate_once()[1] is PolicyDecision.SLEEP
    # Swap to a model that always handovers — Context picks up the new strategy.
    controller.set_strategy(MlBasedStrategy(model=lambda _kpis: PolicyDecision.HANDOVER))
    assert controller.evaluate_once()[1] is PolicyDecision.HANDOVER


def test_get_health_payload_shape() -> None:
    payload = get_health_payload(HealthService("template-app"))
    assert payload["status"] == "OK"
    assert payload["service"] == "template-app"
    assert set(payload) == {"status", "service", "timestamp"}
