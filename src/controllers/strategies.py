"""Strategy pattern — pluggable rApp / xApp optimization algorithms.

Implement :class:`OptimizationStrategy` to swap algorithms without touching
the core rApp framework.

Reference: https://refactoring.guru/design-patterns/strategy
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from models import KpiReport, PolicyDecision


class OptimizationStrategy(ABC):
    """Abstract base for rApp / xApp optimization algorithms.

    :Example:

        >>> strategy = ThresholdBasedStrategy(threshold_low=0.2)
        >>> decision = strategy.evaluate(kpi_report)
    """

    @abstractmethod
    def evaluate(self, kpis: KpiReport) -> PolicyDecision:
        """Evaluate current KPIs and return a policy decision.

        :param kpis: Standardised KPI report from the telemetry collector.
        :return: :class:`~models.PolicyDecision` for the RAN controller.
        """


class ThresholdBasedStrategy(OptimizationStrategy):
    """Rule-based strategy using DL PRB utilization thresholds.

    :param threshold_low: PRB utilization below which the cell is put to sleep
        (`DRB.PrbUtilDL
        <https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/28552-i50.zip>`_
        < ``threshold_low`` → ``SLEEP``, otherwise ``ACTIVE``).

    .. note::

        A second ``threshold_high`` only makes sense with hysteresis (to avoid
        a cell flapping on/off), which requires the cell's current on/off state
        as input. Add it there if needed — a single threshold is sufficient for
        the stateless ``KpiReport → PolicyDecision`` contract.
    """

    def __init__(self, threshold_low: float = 0.2) -> None:
        self.threshold_low = threshold_low

    def evaluate(self, kpis: KpiReport) -> PolicyDecision:
        """Apply PRB utilization threshold rules.

        :param kpis: Standardised KPI report.
        :return: ``SLEEP`` if DL PRB < ``threshold_low``, else ``ACTIVE``.
        """
        if kpis.prb_util_dl < self.threshold_low:
            return PolicyDecision.SLEEP
        return PolicyDecision.ACTIVE


class MlBasedStrategy(OptimizationStrategy):
    """Wraps any callable model returning a :class:`PolicyDecision`.

    Pass a trained model's inference callable as ``model``.  For NVIDIA NIM,
    wrap :class:`NvidiaModelStrategy` instead.

    :param model: Callable ``(KpiReport) → PolicyDecision``.
    """

    def __init__(self, model: Callable[[KpiReport], PolicyDecision]) -> None:
        self._model = model

    def evaluate(self, kpis: KpiReport) -> PolicyDecision:
        """Invoke the wrapped model.

        :param kpis: Standardised KPI report.
        :return: :class:`PolicyDecision` predicted by the model.
        """
        return self._model(kpis)


class NvidiaModelStrategy(OptimizationStrategy):
    """Optimization strategy backed by NVIDIA NeMo / NIM inference.

    Delegates evaluation to a NIM-compatible callable (e.g.
    ``NimAdapter.infer``).  Place all NIM HTTP logic in
    ``src/handlers/nim.py`` and pass the infer callable here —
    strategies must remain I/O-free.

    Security: authenticate via ``Authorization: Bearer <api_key>`` (NVIDIA NIM
    convention).  Pass keys through ``NVIDIA_API_KEY`` env var; never
    hard-code them.  Whitelist only models with known output schemas before
    production use.

    :param nim_infer: Callable ``(KpiReport) → str`` where the return value
        is a :class:`~models.PolicyDecision` string (``"active"``,
        ``"sleep"``, ``"handover"``).  Typically ``NimAdapter.infer``.

    :Example:

        >>> from handlers.nim import NimAdapter   # future adapter
        >>> nim = NimAdapter(
        ...     base_url="https://integrate.api.nvidia.com/v1",
        ...     model_id="nvidia/network-optimization",
        ...     api_key=os.environ["NVIDIA_API_KEY"],
        ... )
        >>> strategy = NvidiaModelStrategy(nim_infer=nim.infer)
        >>> decision = strategy.evaluate(kpi_report)
    """

    def __init__(self, nim_infer: Callable[[KpiReport], str]) -> None:
        self._infer = nim_infer

    def evaluate(self, kpis: KpiReport) -> PolicyDecision:
        """Delegate KPI evaluation to the NVIDIA NIM callable.

        :param kpis: Standardised KPI report.
        :return: :class:`~models.PolicyDecision` from the NIM model.
        :raises ValueError: If the NIM response is not a valid PolicyDecision value.
        """
        result: str = self._infer(kpis)
        return PolicyDecision(result)


#: Built-in strategies selectable by name via ``RAPP_STRATEGY`` (Strategy
#: selection). Algorithms that need an injected model callable
#: (:class:`MlBasedStrategy`, :class:`NvidiaModelStrategy`) are wired explicitly
#: by the composition root, not by name.
_STRATEGIES: dict[str, type[OptimizationStrategy]] = {
    "threshold": ThresholdBasedStrategy,
}


def make_strategy(name: str, **params: float) -> OptimizationStrategy:
    """Construct a built-in optimization strategy by name.

    Mirrors the platform-factory selector (``RAPP_PLATFORM``, which also
    selects the vendor management plane) so every swappable axis is chosen the
    same way.

    :param name: Strategy identifier, e.g. ``"threshold"``.
    :param params: Keyword arguments forwarded to the strategy constructor.
    :return: A configured :class:`OptimizationStrategy`.
    :raises ValueError: If ``name`` is not a registered strategy.
    """
    try:
        factory = _STRATEGIES[name]
    except KeyError:
        raise ValueError(f"Unknown strategy {name!r}. Available: {sorted(_STRATEGIES)}") from None
    return factory(**params)
