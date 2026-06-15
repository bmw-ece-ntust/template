"""Abstract Factory pattern — O-RAN deployment environment component creators.

Each factory creates a compatible set of components for one deployment
environment.  The rApp core logic calls factory methods and never references
concrete classes directly, so environments are swapped by changing
``RAPP_PLATFORM`` in the environment — no code changes required.

Deployment environments
    ``mock``     — :class:`factories.mock.MockPlatformFactory`
                   In-memory no-op components; no external dependencies.
                   Default for unit tests and developer laptops.

    ``osc``      — :class:`factories.osc.OscPlatformFactory`
                   Real O-RAN interfaces (ICS, SME, O1/SDNC).
                   Used for both simulation (pointed at VIAVI RSG O-RAN layer
                   via BMW Lab TA rApp) and production OSC deployments.

    ``physical`` — :class:`factories.physical.PhysicalPlatformFactory`
                   Real gNB testbed with O-RAN SC or vendor management plane.

Simulator note
    Simulation (ns-3, VIAVI RSG) is orchestrated by the BMW Lab TA rApp
    (github.com/bmw-ece-ntust/nonrtric-rapp-test-automation).
    The generic rApp communicates only through O-RAN ALLIANCE protocols
    (O1/A1/R1/E2) — it never calls simulator APIs directly.

Reference: https://refactoring.guru/design-patterns/abstract-factory
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import KpiReport


class ScenarioRunner(ABC):
    """Controls the rApp lifecycle (register with SME, subscribe ICS, start)."""

    @abstractmethod
    def start(self) -> None:
        """Start the scenario / register lifecycle."""

    @abstractmethod
    def stop(self) -> None:
        """Stop the scenario / deregister lifecycle."""


class TelemetryCollector(ABC):
    """Collects raw PM counter data from the platform."""

    @abstractmethod
    def collect(self) -> dict[str, float]:
        """Collect raw telemetry.

        :return: ``{ThreeGPPKpi.value: float}`` mapping.
        """


class KpiAnalyzer(ABC):
    """Converts raw PM data into a standardized :class:`~models.KpiReport`."""

    @abstractmethod
    def analyze(self, raw: dict[str, float]) -> KpiReport:
        """Map raw platform metrics to a standardized KPI report.

        :param raw: Raw metrics from :class:`TelemetryCollector`.
        :return: :class:`~models.KpiReport`.
        """


class RAppPlatformFactory(ABC):
    """Abstract factory for deployment-environment-specific rApp components.

    :Example:

        >>> factory = MockPlatformFactory()
        >>> runner   = factory.create_scenario_runner()
        >>> collector = factory.create_telemetry_collector()
        >>> analyzer  = factory.create_kpi_analyzer()
        >>> runner.start()
    """

    @abstractmethod
    def create_scenario_runner(self) -> ScenarioRunner:
        """Create a :class:`ScenarioRunner` for this environment.

        :return: :class:`ScenarioRunner` implementation.
        """

    @abstractmethod
    def create_telemetry_collector(self) -> TelemetryCollector:
        """Create a :class:`TelemetryCollector` for this environment.

        :return: :class:`TelemetryCollector` implementation.
        """

    @abstractmethod
    def create_kpi_analyzer(self) -> KpiAnalyzer:
        """Create a :class:`KpiAnalyzer` for this environment.

        :return: :class:`KpiAnalyzer` implementation.
        """
