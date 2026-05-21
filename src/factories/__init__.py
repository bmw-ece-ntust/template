"""Abstract Factory pattern — platform-specific rApp component creators.

Implement :class:`RAppPlatformFactory` for each target platform so that
the core rApp logic remains platform-independent.

Supported platforms:

- ``ns3``      — ns-3 simulation environment
- ``viavi``    — VIAVI RSG test equipment
- ``physical`` — Real gNB testbed

Reference: https://refactoring.guru/design-patterns/abstract-factory
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ScenarioRunner(ABC):
    """Abstract scenario runner — controls test or simulation scenario."""

    @abstractmethod
    def start(self) -> None:
        """Start the scenario."""

    @abstractmethod
    def stop(self) -> None:
        """Stop the scenario."""


class TelemetryCollector(ABC):
    """Abstract telemetry collector — collects raw KPI data from the platform."""

    @abstractmethod
    def collect(self) -> dict[str, float]:
        """Collect raw telemetry data.

        :return: Dictionary of raw metric name → value.
        """


class KpiAnalyzer(ABC):
    """Abstract KPI analyzer — processes raw data into standardized KPIs."""

    @abstractmethod
    def analyze(self, raw: dict[str, float]):
        """Convert raw platform metrics to a standardized KpiReport.

        :param raw: Raw metrics from the :class:`TelemetryCollector`.
        :return: :class:`core.models.KpiReport`
        """


class RAppPlatformFactory(ABC):
    """Abstract factory for creating platform-specific rApp components.

    :Example:

        >>> factory = Ns3PlatformFactory()
        >>> runner = factory.create_scenario_runner()
        >>> collector = factory.create_telemetry_collector()
    """

    @abstractmethod
    def create_scenario_runner(self) -> ScenarioRunner:
        """Create a platform-specific scenario runner.

        :return: :class:`ScenarioRunner` implementation for this platform.
        """

    @abstractmethod
    def create_telemetry_collector(self) -> TelemetryCollector:
        """Create a platform-specific telemetry collector.

        :return: :class:`TelemetryCollector` implementation for this platform.
        """

    @abstractmethod
    def create_kpi_analyzer(self) -> KpiAnalyzer:
        """Create a platform-specific KPI analyzer.

        :return: :class:`KpiAnalyzer` implementation for this platform.
        """
