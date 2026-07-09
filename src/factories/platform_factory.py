"""Abstract Factory for deployment-environment-specific rApp components.

Reference: https://refactoring.guru/design-patterns/abstract-factory
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from factories.kpi_analyzer import KpiAnalyzer
from factories.scenario_runner import ScenarioRunner
from factories.telemetry_collector import TelemetryCollector


class RAppPlatformFactory(ABC):
    """Abstract factory for deployment-environment-specific rApp components.

    :Example:

        >>> factory = _build_factory(settings)  # e.g. ViaviPlatformFactory
        >>> runner   = factory.create_scenario_runner()
        >>> collector = factory.create_telemetry_collector()
        >>> analyzer  = factory.create_kpi_analyzer()
        >>> runner.start()
    """

    @abstractmethod
    def create_scenario_runner(self) -> ScenarioRunner:
        """Create a :class:`~factories.ScenarioRunner` for this environment.

        :return: :class:`~factories.ScenarioRunner` implementation.
        """

    @abstractmethod
    def create_telemetry_collector(self) -> TelemetryCollector:
        """Create a :class:`~factories.TelemetryCollector` for this environment.

        :return: :class:`~factories.TelemetryCollector` implementation.
        """

    @abstractmethod
    def create_kpi_analyzer(self) -> KpiAnalyzer:
        """Create a :class:`~factories.KpiAnalyzer` for this environment.

        :return: :class:`~factories.KpiAnalyzer` implementation.
        """
