"""Strategy selector — constructs a built-in strategy from ``RAPP_STRATEGY``."""

from __future__ import annotations

from controllers.strategies.energy_saving_strategy import EnergySavingStrategy
from controllers.strategies.optimization_strategy import OptimizationStrategy
from controllers.strategies.threshold_based_strategy import ThresholdBasedStrategy

#: Built-in strategies selectable by name via ``RAPP_STRATEGY`` (Strategy
#: selection). Algorithms that need an injected model callable
#: (:class:`~controllers.strategies.MlBasedStrategy`,
#: :class:`~controllers.strategies.NvidiaModelStrategy`) are wired explicitly
#: by the composition root, not by name.
_STRATEGIES: dict[str, type[OptimizationStrategy]] = {
    "threshold": ThresholdBasedStrategy,
    "energy-saving": EnergySavingStrategy,
}


def make_strategy(name: str, **params: float) -> OptimizationStrategy:
    """Construct a built-in optimization strategy by name.

    Mirrors the platform-factory selector (``RAPP_PLATFORM``, which also
    selects the vendor management plane) so every swappable axis is chosen the
    same way.

    :param name: Strategy identifier, e.g. ``"threshold"`` or ``"energy-saving"``.
    :param params: Keyword arguments forwarded to the strategy constructor.
    :return: A configured :class:`~controllers.strategies.OptimizationStrategy`.
    :raises ValueError: If ``name`` is not a registered strategy.
    """
    try:
        factory = _STRATEGIES[name]
    except KeyError:
        raise ValueError(f"Unknown strategy {name!r}. Available: {sorted(_STRATEGIES)}") from None
    return factory(**params)
