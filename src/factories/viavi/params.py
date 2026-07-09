"""VIAVI RIC Test proprietary KPI enum and its 3GPP translation table."""

from __future__ import annotations

from enum import Enum

from models.parameters import ThreeGPPKpi, VendorParameterMap


class ViaviParam(str, Enum):
    """VIAVI RIC Test (RSG) KPI names as delivered over the O-RAN interfaces.

    VIAVI mixes 3GPP-shaped counter names (``RRU.*``, ``PEE.*``) with
    proprietary ``Viavi.*`` extensions, following the naming used in the
    O-RAN-Alliance AI/ML challenge energy-saving dataset.  Each member maps
    to a spec-traceable :class:`~models.parameters.ThreeGPPKpi` via
    :data:`VIAVI_PARAM_MAP`; never reference these raw keys outside this
    factory.

    The mapping is illustrative and must be validated against the KPI list
    of the deployed VIAVI RIC Test release before production use.
    """

    PRB_USED_DL = "RRU.PrbUsedDl"  # → DRB.PrbUtilDL (TS 28.552 §5.1.1.12.1)
    PRB_USED_UL = "RRU.PrbUsedUl"  # → DRB.PrbUtilUL (TS 28.552 §5.1.1.12.2)
    THP_DL_KBPS = "DRB.UEThpDl"  # → DRB.UEThpDL (TS 28.552 §5.1.1.10.1)
    THP_UL_KBPS = "DRB.UEThpUl"  # → DRB.UEThpUL (TS 28.552 §5.1.1.10.2)
    RRC_CONN_MEAN = "RRC.ConnMean"  # → RRC.ConnMean (TS 28.552 §5.1.1.1.1)
    AVG_POWER_W = "PEE.AvgPower"  # → PEE.AvgPower (TS 28.552 §5.1.1.19.2.1)
    ENERGY_KWH = "PEE.Energy"  # → PEE.Energy (TS 28.552 §5.1.1.19.3)
    QOS_SCORE = "Viavi.QoS.Score"  # no 3GPP equivalent — intentionally unmapped


#: VIAVI → 3GPP KPI translation table (Adapter pattern).
#: ``QOS_SCORE`` is deliberately absent: keys without a 3GPP equivalent are
#: dropped by :meth:`~models.parameters.VendorParameterMap.raw_to_standard`,
#: so proprietary extras never leak into the rApp core.
VIAVI_PARAM_MAP = VendorParameterMap(
    {
        ViaviParam.PRB_USED_DL.value: ThreeGPPKpi.DRB_PRB_UTIL_DL,
        ViaviParam.PRB_USED_UL.value: ThreeGPPKpi.DRB_PRB_UTIL_UL,
        ViaviParam.THP_DL_KBPS.value: ThreeGPPKpi.DRB_UE_THP_DL,
        ViaviParam.THP_UL_KBPS.value: ThreeGPPKpi.DRB_UE_THP_UL,
        ViaviParam.RRC_CONN_MEAN.value: ThreeGPPKpi.RRC_CONN_MEAN,
        ViaviParam.AVG_POWER_W.value: ThreeGPPKpi.PEE_AVG_POWER,
        ViaviParam.ENERGY_KWH.value: ThreeGPPKpi.PEE_ENERGY,
    }
)
