"""OpenAirInterface (FlexRIC) KPM measurement enum and its 3GPP translation table."""

from __future__ import annotations

from enum import Enum

from models.parameters import ThreeGPPKpi, VendorParameterMap


class OaiParam(str, Enum):
    """OAI gNB E2SM-KPM measurement names as exposed through FlexRIC.

    OAI reports total-PRB counters (``RRU.PrbTot*``) rather than the
    utilization ratios (``DRB.PrbUtil*``) the rApp core consumes, so the
    mapping normalizes naming while the deployment must ensure values are
    ratio-scaled.  Each member maps to a spec-traceable
    :class:`~models.parameters.ThreeGPPKpi` via :data:`OAI_PARAM_MAP`;
    never reference these raw keys outside this factory.

    The mapping is illustrative and must be validated against the KPM
    measurement list of the deployed OAI / FlexRIC release before use.
    """

    PRB_TOT_DL = "RRU.PrbTotDl"  # → DRB.PrbUtilDL (TS 28.552 §5.1.1.12.1)
    PRB_TOT_UL = "RRU.PrbTotUl"  # → DRB.PrbUtilUL (TS 28.552 §5.1.1.12.2)
    THP_DL_KBPS = "DRB.UEThpDl"  # → DRB.UEThpDL (TS 28.552 §5.1.1.10.1)
    THP_UL_KBPS = "DRB.UEThpUl"  # → DRB.UEThpUL (TS 28.552 §5.1.1.10.2)
    RRC_CONN_MEAN = "RRC.ConnMean"  # → RRC.ConnMean (TS 28.552 §5.1.1.1.1)
    PDCP_SDU_VOL_DL = "DRB.PdcpSduVolumeDL"  # volume, not throughput — unmapped


#: OAI → 3GPP KPI translation table (Adapter pattern).
#: ``PDCP_SDU_VOL_DL`` is deliberately absent: a volume counter has no
#: direct :class:`~models.parameters.ThreeGPPKpi` field, so it is dropped
#: rather than silently misread as a throughput.
OAI_PARAM_MAP = VendorParameterMap(
    {
        OaiParam.PRB_TOT_DL.value: ThreeGPPKpi.DRB_PRB_UTIL_DL,
        OaiParam.PRB_TOT_UL.value: ThreeGPPKpi.DRB_PRB_UTIL_UL,
        OaiParam.THP_DL_KBPS.value: ThreeGPPKpi.DRB_UE_THP_DL,
        OaiParam.THP_UL_KBPS.value: ThreeGPPKpi.DRB_UE_THP_UL,
        OaiParam.RRC_CONN_MEAN.value: ThreeGPPKpi.RRC_CONN_MEAN,
    }
)
