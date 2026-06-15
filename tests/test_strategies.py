"""Tests for optimization strategies (Strategy pattern) and the selector."""

from __future__ import annotations

import pytest

from controllers.strategies import (
    MlBasedStrategy,
    ThresholdBasedStrategy,
    make_strategy,
)
from models import KpiReport, PolicyDecision


def test_threshold_strategy_sleeps_when_load_low() -> None:
    strategy = ThresholdBasedStrategy(threshold_low=0.2)
    assert strategy.evaluate(KpiReport("c", prb_util_dl=0.05)) is PolicyDecision.SLEEP


def test_threshold_strategy_active_when_load_high() -> None:
    strategy = ThresholdBasedStrategy(threshold_low=0.2)
    assert strategy.evaluate(KpiReport("c", prb_util_dl=0.9)) is PolicyDecision.ACTIVE


def test_ml_strategy_delegates_to_model() -> None:
    strategy = MlBasedStrategy(model=lambda _kpis: PolicyDecision.HANDOVER)
    assert strategy.evaluate(KpiReport("c")) is PolicyDecision.HANDOVER


def test_make_strategy_builds_registered_strategy() -> None:
    strategy = make_strategy("threshold", threshold_low=0.3)
    assert isinstance(strategy, ThresholdBasedStrategy)
    assert strategy.threshold_low == 0.3


def test_make_strategy_unknown_name_raises() -> None:
    with pytest.raises(ValueError, match="Unknown strategy"):
        make_strategy("does-not-exist")
