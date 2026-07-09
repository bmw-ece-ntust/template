"""OSC Non-RT RIC platform factory — creates components for real O-RAN deployments.

Implements :class:`factories.RAppPlatformFactory` for O-RAN SC Non-RT RIC
environments where telemetry arrives via ICS data subscriptions and
cell configuration is pushed via O1/SDNC.

Platform-component mapping

    .. list-table::
       :header-rows: 1

       * - Abstract component
         - OSC implementation
         - Backing interface
       * - :class:`~factories.ScenarioRunner`
         - :class:`OscLifecycleRunner`
         - R1/SME (register) + R1/ICS (subscribe)
       * - :class:`~factories.TelemetryCollector`
         - :class:`OscIcsTelemetryCollector`
         - R1/ICS job-result polling
       * - :class:`~factories.KpiAnalyzer`
         - :class:`OscKpiAnalyzer`
         - 3GPP PM counter → :class:`~models.KpiReport`

Usage
    Use this factory when ``RAPP_PLATFORM=osc`` is set in the environment.
    For simulation, point it at the simulator's O-RAN interface endpoints
    (see :mod:`factories.ns3` and :mod:`factories.viavi` guidance stubs).

OSC reference
    ``nonrtric/plt/rappmanager``
    https://gerrit.o-ran-sc.org/r/gitweb?p=nonrtric/plt/rappmanager.git

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from factories.osc import OscPlatformFactory``.
"""

from __future__ import annotations

from factories.osc.factory import OscPlatformFactory
from factories.osc.kpi_analyzer import OscKpiAnalyzer
from factories.osc.lifecycle_runner import OscLifecycleRunner
from factories.osc.telemetry_collector import OscIcsTelemetryCollector

__all__ = [
    "OscIcsTelemetryCollector",
    "OscKpiAnalyzer",
    "OscLifecycleRunner",
    "OscPlatformFactory",
]
