"""ns-3 simulation platform factory.

Implements :class:`factories.RAppPlatformFactory` for the ns-3 discrete-event
network simulator.
"""

from __future__ import annotations

from factories import KpiAnalyzer, RAppPlatformFactory, ScenarioRunner, TelemetryCollector


class Ns3ScenarioRunner(ScenarioRunner):
    """Controls an ns-3 simulation scenario."""

    def start(self) -> None:
        """Start the ns-3 simulation.

        :raises NotImplementedError: Replace with ns-3 scenario start logic.
        """
        raise NotImplementedError("Implement ns-3 scenario start logic.")

    def stop(self) -> None:
        """Stop the ns-3 simulation.

        :raises NotImplementedError: Replace with ns-3 scenario stop logic.
        """
        raise NotImplementedError("Implement ns-3 scenario stop logic.")


class Ns3TelemetryCollector(TelemetryCollector):
    """Collects raw telemetry from an ns-3 simulation output."""

    def collect(self) -> dict[str, float]:
        """Read ns-3 trace files and return raw metrics.

        :return: Dictionary of raw metric name → value.
        :raises NotImplementedError: Replace with ns-3 telemetry parsing.
        """
        raise NotImplementedError("Implement ns-3 telemetry collection.")


class Ns3KpiAnalyzer(KpiAnalyzer):
    """Converts ns-3 raw output into a standardized KpiReport."""

    def analyze(self, raw: dict[str, float]):
        """Map ns-3 column names to 3GPP KPI names.

        :param raw: Raw ns-3 metrics dictionary.
        :return: :class:`core.models.KpiReport`
        :raises NotImplementedError: Replace with ns-3 KPI mapping logic.
        """
        raise NotImplementedError("Implement ns-3 KPI mapping.")


class Ns3PlatformFactory(RAppPlatformFactory):
    """Factory for the ns-3 simulation environment."""

    def create_scenario_runner(self) -> ScenarioRunner:
        """Create an ns-3 scenario runner.

        :return: :class:`Ns3ScenarioRunner`
        """
        return Ns3ScenarioRunner()

    def create_telemetry_collector(self) -> TelemetryCollector:
        """Create an ns-3 telemetry collector.

        :return: :class:`Ns3TelemetryCollector`
        """
        return Ns3TelemetryCollector()

    def create_kpi_analyzer(self) -> KpiAnalyzer:
        """Create an ns-3 KPI analyzer.

        :return: :class:`Ns3KpiAnalyzer`
        """
        return Ns3KpiAnalyzer()
