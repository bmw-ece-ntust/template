"""Ericsson vendor adapter — proprietary counters → 3GPP KPIs.

Ericsson RAN exposes performance counters under proprietary PM names (the
``pmEgress*`` / ``pm*`` families) that differ from the 3GPP TS 28.552 counter
names this template's core logic expects.  :class:`EricssonParam` enumerates the
proprietary names; :data:`ERICSSON_PARAM_MAP` translates them to
:class:`~models.parameters.ThreeGPPKpi`.

The proprietary-name to 3GPP-name mapping below is illustrative and must be
validated against the Ericsson PM Counter reference for the deployed RAN
software level before production use.

Reference: https://refactoring.guru/design-patterns/adapter
"""

from __future__ import annotations

from enum import Enum
from typing import ClassVar

from handlers.adapters import VendorAdapter
from models.parameters import NodeType, ThreeGPPKpi, VendorParameterMap


class EricssonParam(str, Enum):
    """Ericsson proprietary PM counter names.

    Each member maps to a spec-traceable
    :class:`~models.parameters.ThreeGPPKpi` via
    :data:`ERICSSON_PARAM_MAP`.  Values are the raw keys Ericsson telemetry
    returns; never reference them outside this adapter.
    """

    PRB_USAGE_DL_PCT = "pmPrbUtilDl"  # → DRB.PrbUtilDL (TS 28.552 §5.1.1.12.1)
    PRB_USAGE_UL_PCT = "pmPrbUtilUl"  # → DRB.PrbUtilUL (TS 28.552 §5.1.1.12.2)
    RRC_CONN_AVG = "pmRrcConnLevAvg"  # → RRC.ConnMean (TS 28.552 §5.1.1.1.1)
    THP_DL_KBPS = "pmPdcpVolDlDrbKbps"  # → DRB.UEThpDL (TS 28.552 §5.1.1.10.1)
    THP_UL_KBPS = "pmPdcpVolUlDrbKbps"  # → DRB.UEThpUL (TS 28.552 §5.1.1.10.2)
    RSRP_DBM = "pmRadioRsrpAvg"  # → RSRP (TS 36.214 §5.1.1)
    SINR_DB = "pmRadioSinrAvg"  # → SINR (TS 36.214 §5.1.4)


#: Ericsson proprietary → 3GPP KPI translation table (Adapter pattern).
ERICSSON_PARAM_MAP = VendorParameterMap(
    {
        EricssonParam.PRB_USAGE_DL_PCT.value: ThreeGPPKpi.DRB_PRB_UTIL_DL,
        EricssonParam.PRB_USAGE_UL_PCT.value: ThreeGPPKpi.DRB_PRB_UTIL_UL,
        EricssonParam.RRC_CONN_AVG.value: ThreeGPPKpi.RRC_CONN_MEAN,
        EricssonParam.THP_DL_KBPS.value: ThreeGPPKpi.DRB_UE_THP_DL,
        EricssonParam.THP_UL_KBPS.value: ThreeGPPKpi.DRB_UE_THP_UL,
        EricssonParam.RSRP_DBM.value: ThreeGPPKpi.RSRP,
        EricssonParam.SINR_DB.value: ThreeGPPKpi.SINR,
    }
)


class EricssonTelemetryAdapter(VendorAdapter):
    """Adapts Ericsson proprietary telemetry to a standard KPI report.

    :Example:

        >>> adapter = EricssonTelemetryAdapter(ericsson_client)
        >>> report = adapter.to_kpi_report("cell-001", gnb_id="gnb-er-1")
        >>> report.prb_util_dl  # normalized from pmPrbUtilDl
    """

    VENDOR: ClassVar[str] = "ericsson"
    PARAM_MAP: ClassVar[VendorParameterMap] = ERICSSON_PARAM_MAP
    NODE_TYPE: ClassVar[NodeType] = NodeType.GNB
