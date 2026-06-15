"""3GPP-aligned KPI data models for rApp/xApp core logic.

All parameters are linked to authoritative specifications per
BMW Lab SOP source-code-guide §8.

TS 28.552: https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/28552-i50.zip
TS 36.214: https://www.3gpp.org/ftp/Specs/archive/36_series/36.214/36214-i40.zip
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar

from models.parameters import NodeType, ThreeGPPKpi  # re-exported


class PolicyDecision(Enum):
    """RAN policy decision output from the optimization strategy."""

    ACTIVE = "active"
    SLEEP = "sleep"
    HANDOVER = "handover"


@dataclass(frozen=True)
class KpiReport:
    """Standardized 3GPP KPI report consumed by optimization strategies.

    New fields default to ``0`` / ``0.0`` / ``None`` so existing callers
    that only pass ``cell_id``, ``prb_util_dl``, ``prb_util_ul``, and
    ``active_ue_count`` continue to work without modification.

    :param cell_id: NR Cell Global ID (e.g. ``"o-du-1111/cell-0"``).
    :param gnb_id: Parent gNB or access-point identifier.
        Used to group cells in :class:`~models.topology.NetworkTopology`.
    :param node_type: :class:`~models.parameters.NodeType` —
        ``GNB``, ``ENODEB``, or ``WIFI_AP``.
    :param prb_util_dl:
        DL PRB utilization ratio
        (`DRB.PrbUtilDL
        <https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/28552-i50.zip>`_,
        TS 28.552 §5.1.1.12.1, Table 5.1.1.12.1-1, p.47).
    :param prb_util_ul:
        UL PRB utilization ratio
        (`DRB.PrbUtilUL
        <https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/28552-i50.zip>`_,
        TS 28.552 §5.1.1.12.2, Table 5.1.1.12.2-1, p.48).
    :param active_ue_count:
        Mean RRC-connected UE count
        (`RRC.ConnMean
        <https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/28552-i50.zip>`_,
        TS 28.552 §5.1.1.1.1, Table 5.1.1.1.1-1, p.21).
    :param dl_throughput_kbps:
        Mean DL UE throughput in kbps
        (`DRB.UEThpDL
        <https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/28552-i50.zip>`_,
        TS 28.552 §5.1.1.10.1, Table 5.1.1.10.1-1, p.44).
    :param ul_throughput_kbps:
        Mean UL UE throughput in kbps
        (`DRB.UEThpUL
        <https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/28552-i50.zip>`_,
        TS 28.552 §5.1.1.10.2, Table 5.1.1.10.2-1, p.45).
    :param rsrp_dbm:
        Reference Signal Received Power in dBm
        (`RSRP
        <https://www.3gpp.org/ftp/Specs/archive/36_series/36.214/36214-i40.zip>`_,
        TS 36.214 §5.1.1, p.9).  ``None`` for WiFi APs.
    :param rsrq_db:
        Reference Signal Received Quality in dB
        (`RSRQ
        <https://www.3gpp.org/ftp/Specs/archive/36_series/36.214/36214-i40.zip>`_,
        TS 36.214 §5.1.2, p.10).  ``None`` for WiFi APs.
    :param sinr_db:
        Signal-to-Interference-plus-Noise Ratio in dB
        (`SINR
        <https://www.3gpp.org/ftp/Specs/archive/36_series/36.214/36214-i40.zip>`_,
        TS 36.214 §5.1.4, p.12).  ``None`` for WiFi APs.
    """

    cell_id: str
    gnb_id: str = ""
    node_type: NodeType = NodeType.GNB
    prb_util_dl: float = 0.0
    prb_util_ul: float = 0.0
    active_ue_count: int = 0
    dl_throughput_kbps: float = 0.0
    ul_throughput_kbps: float = 0.0
    rsrp_dbm: float | None = None
    rsrq_db: float | None = None
    sinr_db: float | None = None

    #: Mapping from :class:`ThreeGPPKpi` to the matching constructor field.
    #: Single source of truth for vendor adapters and E2/ICS parsers.
    _FIELD_BY_KPI: ClassVar[dict[ThreeGPPKpi, str]] = {
        ThreeGPPKpi.DRB_PRB_UTIL_DL: "prb_util_dl",
        ThreeGPPKpi.DRB_PRB_UTIL_UL: "prb_util_ul",
        ThreeGPPKpi.RRC_CONN_MEAN: "active_ue_count",
        ThreeGPPKpi.DRB_UE_THP_DL: "dl_throughput_kbps",
        ThreeGPPKpi.DRB_UE_THP_UL: "ul_throughput_kbps",
        ThreeGPPKpi.RSRP: "rsrp_dbm",
        ThreeGPPKpi.RSRQ: "rsrq_db",
        ThreeGPPKpi.SINR: "sinr_db",
    }

    @classmethod
    def from_3gpp(
        cls,
        cell_id: str,
        values: dict[ThreeGPPKpi, float],
        *,
        gnb_id: str = "",
        node_type: NodeType = NodeType.GNB,
    ) -> KpiReport:
        """Build a report from a 3GPP-keyed value dict.

        This is the canonical bridge from any standardized
        ``{ThreeGPPKpi: value}`` mapping (produced by a vendor
        :class:`~models.parameters.VendorParameterMap` or an E2/ICS
        parser) to a typed :class:`KpiReport`.  Unknown keys are ignored;
        ``active_ue_count`` is coerced to ``int``.

        :param cell_id: NR Cell Global ID.
        :param values: ``{ThreeGPPKpi: value}`` standardized telemetry.
        :param gnb_id: Parent gNB identifier.
        :param node_type: :class:`~models.parameters.NodeType`.
        :return: Populated :class:`KpiReport`.
        """
        fields: dict[str, Any] = {}
        for kpi, value in values.items():
            field = cls._FIELD_BY_KPI.get(kpi)
            if field is None:
                continue
            fields[field] = int(value) if field == "active_ue_count" else float(value)
        return cls(cell_id=cell_id, gnb_id=gnb_id, node_type=node_type, **fields)
