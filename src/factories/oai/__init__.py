"""OAI platform factory — OpenAirInterface KPM naming → 3GPP ``KpiReport``.

Selected via ``RAPP_PLATFORM=oai``.  OpenAirInterface gNBs attach to the RIC
through FlexRIC's standard E2 interface, so this factory reuses the OSC
SME/ICS transport and swaps in only the Adapter: :class:`OaiKpiAnalyzer`
translates OAI measurement names (``RRU.PrbTotDl``, ``DRB.PdcpSduVolumeDL``,
…) to spec-traceable :class:`~models.parameters.ThreeGPPKpi` via
:data:`OAI_PARAM_MAP`, so the rApp core never sees OAI names.

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from factories.oai import OaiParam, OaiPlatformFactory``.

References
    Abstract Factory: https://refactoring.guru/design-patterns/abstract-factory
    Adapter:          https://refactoring.guru/design-patterns/adapter
    OpenAirInterface: https://openairinterface.org/
    FlexRIC:          https://gitlab.eurecom.fr/mosaic5g/flexric
"""

from __future__ import annotations

from factories.oai.factory import OaiPlatformFactory
from factories.oai.kpi_analyzer import OaiKpiAnalyzer
from factories.oai.params import OAI_PARAM_MAP, OaiParam

__all__ = [
    "OAI_PARAM_MAP",
    "OaiKpiAnalyzer",
    "OaiParam",
    "OaiPlatformFactory",
]
