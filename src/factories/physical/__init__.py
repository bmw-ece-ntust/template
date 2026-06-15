"""Physical gNB testbed platform factory.

Implements :class:`factories.RAppPlatformFactory` for a real gNB testbed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from factories import KpiAnalyzer, RAppPlatformFactory, ScenarioRunner, TelemetryCollector

if TYPE_CHECKING:
    from models import KpiReport


class PhysicalScenarioRunner(ScenarioRunner):
    """Controls a physical gNB testbed scenario."""

    def start(self) -> None:
        """Start the physical testbed scenario.

        :raises NotImplementedError: Replace with testbed start logic.
        """
        raise NotImplementedError("Implement physical testbed scenario start logic.")

    def stop(self) -> None:
        """Stop the physical testbed scenario.

        :raises NotImplementedError: Replace with testbed stop logic.
        """
        raise NotImplementedError("Implement physical testbed scenario stop logic.")


class PhysicalTelemetryCollector(TelemetryCollector):
    """Collects raw telemetry from a real gNB testbed."""

    def collect(self) -> dict[str, float]:
        """Read gNB telemetry via O1/E2 interface.

        :return: Dictionary of raw metric name → value.
        :raises NotImplementedError: Replace with physical testbed telemetry logic.
        """
        raise NotImplementedError("Implement physical testbed telemetry collection.")


class PhysicalKpiAnalyzer(KpiAnalyzer):
    """Converts physical gNB telemetry into a standardized KpiReport."""

    def analyze(self, raw: dict[str, float]) -> KpiReport:
        """Map gNB telemetry fields to 3GPP KPI names.

        :param raw: Raw gNB metrics dictionary.
        :return: :class:`models.KpiReport`
        :raises NotImplementedError: Replace with physical testbed KPI mapping.
        """
        raise NotImplementedError("Implement physical testbed KPI mapping.")


class PhysicalPlatformFactory(RAppPlatformFactory):
    """Factory for real gNB testbed."""

    def create_scenario_runner(self) -> ScenarioRunner:
        """Create a physical testbed scenario runner.

        :return: :class:`PhysicalScenarioRunner`
        """
        return PhysicalScenarioRunner()

    def create_telemetry_collector(self) -> TelemetryCollector:
        """Create a physical testbed telemetry collector.

        :return: :class:`PhysicalTelemetryCollector`
        """
        return PhysicalTelemetryCollector()

    def create_kpi_analyzer(self) -> KpiAnalyzer:
        """Create a physical testbed KPI analyzer.

        :return: :class:`PhysicalKpiAnalyzer`
        """
        return PhysicalKpiAnalyzer()
