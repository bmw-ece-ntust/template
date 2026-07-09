"""Abstract Factory pattern — O-RAN deployment environment component creators.

Each factory creates a compatible set of components for one deployment
environment.  The rApp core logic calls factory methods and never references
concrete classes directly, so environments are swapped by changing
``RAPP_PLATFORM`` in the environment — no code changes required.

Deployment platforms
    ``osc``   — :class:`factories.osc.OscPlatformFactory`
                Real O-RAN interfaces (ICS, SME, O1/SDNC) with pure 3GPP
                counter names; no vendor translation.  Default.

    ``ns3``   — :class:`factories.ns3.Ns3PlatformFactory`
                ns-3 simulation via ns-O-RAN; OSC transport plus the
                ns-O-RAN naming Adapter.

    ``viavi`` — :class:`factories.viavi.ViaviPlatformFactory`
                VIAVI RIC Test (RSG); OSC transport plus the VIAVI naming
                Adapter (includes PEE energy counters).

    ``oai``   — :class:`factories.oai.OaiPlatformFactory`
                OpenAirInterface gNBs via FlexRIC; OSC transport plus the
                OAI naming Adapter.

    ``ocudu`` — :class:`factories.ocudu.OcuduPlatformFactory`
                Linux Foundation OCUDU (srsRAN-lineage CU/DU); OSC transport
                plus the OCUDU naming and unit Adapter.

Vendor factories subclass :class:`factories.osc.OscPlatformFactory` and
override only ``create_kpi_analyzer()``: every supported stack speaks
standard O-RAN interfaces, so vendors differ solely in the parameter
Adapter, never in transport.

Simulator note
    Simulation lifecycle (ns-3, VIAVI RSG) is orchestrated by the BMW Lab
    TA rApp (github.com/bmw-ece-ntust/nonrtric-rapp-test-automation).
    The generic rApp communicates only through O-RAN ALLIANCE protocols
    (O1/A1/R1/E2) — it never calls simulator APIs directly.

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from factories import RAppPlatformFactory``.

Reference: https://refactoring.guru/design-patterns/abstract-factory
"""

from __future__ import annotations

from factories.kpi_analyzer import KpiAnalyzer
from factories.platform_factory import RAppPlatformFactory
from factories.scenario_runner import ScenarioRunner
from factories.telemetry_collector import TelemetryCollector

__all__ = [
    "KpiAnalyzer",
    "RAppPlatformFactory",
    "ScenarioRunner",
    "TelemetryCollector",
]
