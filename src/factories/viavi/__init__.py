"""VIAVI RSG test-equipment platform factory.

Implements :class:`factories.RAppPlatformFactory` for VIAVI RSG test equipment.
"""

from __future__ import annotations

from factories import KpiAnalyzer, RAppPlatformFactory, ScenarioRunner, TelemetryCollector


class ViaviScenarioRunner(ScenarioRunner):
    """Controls a VIAVI RSG test scenario."""

    def start(self) -> None:
        """Start the VIAVI scenario.

        :raises NotImplementedError: Replace with VIAVI scenario start logic.
        """
        raise NotImplementedError("Implement VIAVI scenario start logic.")

    def stop(self) -> None:
        """Stop the VIAVI scenario.

        :raises NotImplementedError: Replace with VIAVI scenario stop logic.
        """
        raise NotImplementedError("Implement VIAVI scenario stop logic.")


class ViaviTelemetryCollector(TelemetryCollector):
    """Collects raw telemetry from VIAVI RSG output."""

    def collect(self) -> dict[str, float]:
        """Read VIAVI RSG metrics and return raw data.

        :return: Dictionary of raw metric name → value.
        :raises NotImplementedError: Replace with VIAVI telemetry parsing.
        """
        raise NotImplementedError("Implement VIAVI telemetry collection.")


class ViaviKpiAnalyzer(KpiAnalyzer):
    """Converts VIAVI RSG output into a standardized KpiReport."""

    def analyze(self, raw: dict[str, float]):
        """Map VIAVI metric names to 3GPP KPI names.

        :param raw: Raw VIAVI metrics dictionary.
        :return: :class:`core.models.KpiReport`
        :raises NotImplementedError: Replace with VIAVI KPI mapping logic.
        """
        raise NotImplementedError("Implement VIAVI KPI mapping.")


class ViaviPlatformFactory(RAppPlatformFactory):
    """Factory for VIAVI RSG test equipment."""

    def create_scenario_runner(self) -> ScenarioRunner:
        """Create a VIAVI scenario runner.

        :return: :class:`ViaviScenarioRunner`
        """
        return ViaviScenarioRunner()

    def create_telemetry_collector(self) -> TelemetryCollector:
        """Create a VIAVI telemetry collector.

        :return: :class:`ViaviTelemetryCollector`
        """
        return ViaviTelemetryCollector()

    def create_kpi_analyzer(self) -> KpiAnalyzer:
        """Create a VIAVI KPI analyzer.

        :return: :class:`ViaviKpiAnalyzer`
        """
        return ViaviKpiAnalyzer()
