"""VIAVI platform factory — RIC Test KPI naming → 3GPP ``KpiReport``.

Selected via ``RAPP_PLATFORM=viavi``.  VIAVI RIC Test (RSG) exposes standard
O-RAN interfaces, so this factory reuses the OSC SME/ICS transport and swaps
in only the Adapter: :class:`ViaviKpiAnalyzer` translates VIAVI KPI names
(``RRU.PrbUsedDl``, ``PEE.AvgPower``, ``Viavi.QoS.Score``, …) to
spec-traceable :class:`~models.parameters.ThreeGPPKpi` via
:data:`VIAVI_PARAM_MAP`, so the rApp core never sees vendor names.

Simulator lifecycle is orchestrated by the BMW Lab TA rApp
(github.com/bmw-ece-ntust/nonrtric-rapp-test-automation); the rApp itself
communicates only through O-RAN ALLIANCE protocols.

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from factories.viavi import ViaviParam, ViaviPlatformFactory``.

References
    Abstract Factory: https://refactoring.guru/design-patterns/abstract-factory
    Adapter:          https://refactoring.guru/design-patterns/adapter
    VIAVI RIC Test:   https://www.viavisolutions.com/en-us/products/ric-test
"""

from __future__ import annotations

from factories.viavi.factory import ViaviPlatformFactory
from factories.viavi.kpi_analyzer import ViaviKpiAnalyzer
from factories.viavi.params import VIAVI_PARAM_MAP, ViaviParam

__all__ = [
    "VIAVI_PARAM_MAP",
    "ViaviKpiAnalyzer",
    "ViaviParam",
    "ViaviPlatformFactory",
]
