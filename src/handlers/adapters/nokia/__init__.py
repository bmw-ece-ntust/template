"""Nokia vendor adapter — proprietary counters → 3GPP KPIs.

Nokia AirScale RAN exposes performance counters under proprietary ``M8*`` /
``NR*`` PM names that differ from the 3GPP TS 28.552 names this template's core
logic expects.  :class:`NokiaParam` enumerates the proprietary names;
:data:`NOKIA_PARAM_MAP` translates them to
:class:`~models.parameters.ThreeGPPKpi`.

The proprietary-name to 3GPP-name mapping below is illustrative and must be
validated against the Nokia PM Counter reference for the deployed RAN software
level before production use.

Reference: https://refactoring.guru/design-patterns/adapter
"""

from __future__ import annotations

from enum import Enum
from typing import ClassVar

from handlers.adapters import VendorAdapter
from models.parameters import NodeType, ThreeGPPKpi, VendorParameterMap


class NokiaParam(str, Enum):
    """Nokia proprietary PM counter names.

    Each member maps to a spec-traceable
    :class:`~models.parameters.ThreeGPPKpi` via :data:`NOKIA_PARAM_MAP`.
    """

    PRB_UTIL_DL = "NR_PrbUsedDlPct"  # → DRB.PrbUtilDL (TS 28.552 §5.1.1.12.1)
    PRB_UTIL_UL = "NR_PrbUsedUlPct"  # → DRB.PrbUtilUL (TS 28.552 §5.1.1.12.2)
    CONN_UE_AVG = "NR_RrcConnUeAvg"  # → RRC.ConnMean (TS 28.552 §5.1.1.1.1)
    THP_DL_KBPS = "NR_DlThpVolKbps"  # → DRB.UEThpDL (TS 28.552 §5.1.1.10.1)
    THP_UL_KBPS = "NR_UlThpVolKbps"  # → DRB.UEThpUL (TS 28.552 §5.1.1.10.2)
    RSRP_DBM = "NR_RsrpMeanDbm"  # → RSRP (TS 36.214 §5.1.1)
    RSRQ_DB = "NR_RsrqMeanDb"  # → RSRQ (TS 36.214 §5.1.2)


#: Nokia proprietary → 3GPP KPI translation table (Adapter pattern).
NOKIA_PARAM_MAP = VendorParameterMap(
    {
        NokiaParam.PRB_UTIL_DL.value: ThreeGPPKpi.DRB_PRB_UTIL_DL,
        NokiaParam.PRB_UTIL_UL.value: ThreeGPPKpi.DRB_PRB_UTIL_UL,
        NokiaParam.CONN_UE_AVG.value: ThreeGPPKpi.RRC_CONN_MEAN,
        NokiaParam.THP_DL_KBPS.value: ThreeGPPKpi.DRB_UE_THP_DL,
        NokiaParam.THP_UL_KBPS.value: ThreeGPPKpi.DRB_UE_THP_UL,
        NokiaParam.RSRP_DBM.value: ThreeGPPKpi.RSRP,
        NokiaParam.RSRQ_DB.value: ThreeGPPKpi.RSRQ,
    }
)


class NokiaTelemetryAdapter(VendorAdapter):
    """Adapts Nokia proprietary telemetry to a standard KPI report.

    :Example:

        >>> adapter = NokiaTelemetryAdapter(nokia_client)
        >>> report = adapter.to_kpi_report("cell-002", gnb_id="gnb-nok-1")
    """

    VENDOR: ClassVar[str] = "nokia"
    PARAM_MAP: ClassVar[VendorParameterMap] = NOKIA_PARAM_MAP
    NODE_TYPE: ClassVar[NodeType] = NodeType.GNB
