"""Strategy pattern — pluggable rApp / xApp optimization algorithms.

Implement :class:`OptimizationStrategy` to swap algorithms without touching
the core rApp framework.

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from controllers.strategies import ThresholdBasedStrategy, make_strategy``.

Reference: https://refactoring.guru/design-patterns/strategy
"""

from __future__ import annotations

from controllers.strategies.energy_saving_strategy import EnergySavingStrategy
from controllers.strategies.ml_based_strategy import MlBasedStrategy
from controllers.strategies.nvidia_model_strategy import NvidiaModelStrategy
from controllers.strategies.optimization_strategy import OptimizationStrategy
from controllers.strategies.selector import make_strategy
from controllers.strategies.threshold_based_strategy import ThresholdBasedStrategy

__all__ = [
    "EnergySavingStrategy",
    "MlBasedStrategy",
    "NvidiaModelStrategy",
    "OptimizationStrategy",
    "ThresholdBasedStrategy",
    "make_strategy",
]
