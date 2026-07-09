"""ns-3 platform factory — ns-O-RAN KPM naming → 3GPP ``KpiReport``.

Selected via ``RAPP_PLATFORM=ns3``.  ns-O-RAN exposes ns-3 simulated gNBs
through standard O-RAN interfaces, so this factory reuses the OSC SME/ICS
transport and swaps in only the Adapter: :class:`Ns3KpiAnalyzer` translates
ns-O-RAN measurement names (``RRU.PrbUsedDl``, ``L3servingSINR``, …) to
spec-traceable :class:`~models.parameters.ThreeGPPKpi` via
:data:`NS3_PARAM_MAP`, so the rApp core never sees simulator names.

Simulation lifecycle is orchestrated by the BMW Lab TA rApp
(github.com/bmw-ece-ntust/nonrtric-rapp-test-automation); the rApp itself
communicates only through O-RAN ALLIANCE protocols.

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from factories.ns3 import Ns3Param, Ns3PlatformFactory``.

References
    Abstract Factory: https://refactoring.guru/design-patterns/abstract-factory
    Adapter:          https://refactoring.guru/design-patterns/adapter
    ns-O-RAN:         https://openrangym.com/ran-frameworks/ns-o-ran
"""

from __future__ import annotations

from factories.ns3.factory import Ns3PlatformFactory
from factories.ns3.kpi_analyzer import Ns3KpiAnalyzer
from factories.ns3.params import NS3_PARAM_MAP, Ns3Param

__all__ = [
    "NS3_PARAM_MAP",
    "Ns3KpiAnalyzer",
    "Ns3Param",
    "Ns3PlatformFactory",
]
