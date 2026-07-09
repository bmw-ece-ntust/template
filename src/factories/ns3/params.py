"""ns-3 (ns-O-RAN) KPM measurement enum and its 3GPP translation table."""

from __future__ import annotations

from enum import Enum

from models.parameters import ThreeGPPKpi, VendorParameterMap


class Ns3Param(str, Enum):
    """ns-O-RAN E2SM-KPM measurement names reported by the ns-3 E2 nodes.

    ns-O-RAN reports a mix of 3GPP-shaped counters (``RRU.*``, ``DRB.*``)
    and custom L3 measurements.  Each member maps to a spec-traceable
    :class:`~models.parameters.ThreeGPPKpi` via :data:`NS3_PARAM_MAP`;
    never reference these raw keys outside this factory.

    The mapping is illustrative and must be validated against the KPM report
    definition of the deployed ns-O-RAN build before use.
    """

    PRB_USED_DL = "RRU.PrbUsedDl"  # → DRB.PrbUtilDL (TS 28.552 §5.1.1.12.1)
    PRB_USED_UL = "RRU.PrbUsedUl"  # → DRB.PrbUtilUL (TS 28.552 §5.1.1.12.2)
    THP_DL_KBPS = "DRB.UEThpDl"  # → DRB.UEThpDL (TS 28.552 §5.1.1.10.1)
    THP_UL_KBPS = "DRB.UEThpUl"  # → DRB.UEThpUL (TS 28.552 §5.1.1.10.2)
    MEAN_ACTIVE_UE_DL = "DRB.MeanActiveUeDl"  # → RRC.ConnMean (TS 28.552 §5.1.1.1.1)
    SERVING_SINR = "L3servingSINR"  # → SINR (TS 36.214 §5.1.4)


#: ns-O-RAN → 3GPP KPI translation table (Adapter pattern).
NS3_PARAM_MAP = VendorParameterMap(
    {
        Ns3Param.PRB_USED_DL.value: ThreeGPPKpi.DRB_PRB_UTIL_DL,
        Ns3Param.PRB_USED_UL.value: ThreeGPPKpi.DRB_PRB_UTIL_UL,
        Ns3Param.THP_DL_KBPS.value: ThreeGPPKpi.DRB_UE_THP_DL,
        Ns3Param.THP_UL_KBPS.value: ThreeGPPKpi.DRB_UE_THP_UL,
        Ns3Param.MEAN_ACTIVE_UE_DL.value: ThreeGPPKpi.RRC_CONN_MEAN,
        Ns3Param.SERVING_SINR.value: ThreeGPPKpi.SINR,
    }
)
