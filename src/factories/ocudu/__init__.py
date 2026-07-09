"""OCUDU platform factory — open CU/DU metric naming → 3GPP ``KpiReport``.

Selected via ``RAPP_PLATFORM=ocudu``.  OCUDU (the Linux Foundation
open-source CU/DU built on the srsRAN 5G stack) attaches to the RIC through
its standard E2 agent, so this factory reuses the OSC SME/ICS transport and
swaps in only the Adapter: :class:`OcuduKpiAnalyzer` translates OCUDU metric
names and units (``dl_brate`` in bit/s, ``pusch_snr_db``, …) to
spec-traceable :class:`~models.parameters.ThreeGPPKpi` via
:data:`OCUDU_PARAM_MAP`, so the rApp core never sees stack-specific names.

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from factories.ocudu import OcuduParam, OcuduPlatformFactory``.

References
    Abstract Factory: https://refactoring.guru/design-patterns/abstract-factory
    Adapter:          https://refactoring.guru/design-patterns/adapter
    OCUDU:            https://ocudu.org/
"""

from __future__ import annotations

from factories.ocudu.factory import OcuduPlatformFactory
from factories.ocudu.kpi_analyzer import OcuduKpiAnalyzer
from factories.ocudu.params import OCUDU_PARAM_MAP, OcuduParam

__all__ = [
    "OCUDU_PARAM_MAP",
    "OcuduKpiAnalyzer",
    "OcuduParam",
    "OcuduPlatformFactory",
]
