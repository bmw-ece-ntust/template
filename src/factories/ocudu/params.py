"""OCUDU (Linux Foundation open CU/DU) metric enum and its 3GPP translation table."""

from __future__ import annotations

from enum import Enum

from models.parameters import ThreeGPPKpi, VendorParameterMap


class OcuduParam(str, Enum):
    """OCUDU gNB metric names as reported by the srsRAN-lineage metrics stream.

    OCUDU (the Linux Foundation open-source CU/DU built on the srsRAN 5G
    stack) reports flat ``snake_case`` metric keys.  Each member maps to a
    spec-traceable :class:`~models.parameters.ThreeGPPKpi` via
    :data:`OCUDU_PARAM_MAP`; never reference these raw keys outside this
    factory.

    Bitrates arrive in bit/s and are rescaled to kbps by
    :class:`~factories.ocudu.OcuduKpiAnalyzer` — the map handles naming
    only.  The mapping is illustrative and must be validated against the
    metrics reference of the deployed OCUDU release before use.
    """

    DL_BITRATE_BPS = "dl_brate"  # → DRB.UEThpDL (TS 28.552 §5.1.1.10.1), bit/s
    UL_BITRATE_BPS = "ul_brate"  # → DRB.UEThpUL (TS 28.552 §5.1.1.10.2), bit/s
    UE_COUNT = "ue_count"  # → RRC.ConnMean (TS 28.552 §5.1.1.1.1)
    RSRP_DBM = "rsrp"  # → RSRP (TS 36.214 §5.1.1)
    PUSCH_SNR_DB = "pusch_snr_db"  # → SINR (TS 36.214 §5.1.4)


#: OCUDU → 3GPP KPI translation table (Adapter pattern).
OCUDU_PARAM_MAP = VendorParameterMap(
    {
        OcuduParam.DL_BITRATE_BPS.value: ThreeGPPKpi.DRB_UE_THP_DL,
        OcuduParam.UL_BITRATE_BPS.value: ThreeGPPKpi.DRB_UE_THP_UL,
        OcuduParam.UE_COUNT.value: ThreeGPPKpi.RRC_CONN_MEAN,
        OcuduParam.RSRP_DBM.value: ThreeGPPKpi.RSRP,
        OcuduParam.PUSCH_SNR_DB.value: ThreeGPPKpi.SINR,
    }
)
