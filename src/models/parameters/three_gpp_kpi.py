"""3GPP performance-measurement counter identifier enum.

TS 28.552 (PM counters):
    https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/28552-i50.zip
TS 36.214 (Radio measurements):
    https://www.3gpp.org/ftp/Specs/archive/36_series/36.214/36214-i40.zip
TS 28.532 (Generic management services / VES):
    https://www.3gpp.org/ftp/Specs/archive/28_series/28.532/28532-i50.zip
"""

from __future__ import annotations

from enum import Enum


class ThreeGPPKpi(str, Enum):
    """3GPP performance-measurement counter identifiers.

    Values are the canonical counter names used in O-RAN ICS deliveries,
    VES PM files, and NETCONF PM data models.  Use ``.value`` to obtain
    the raw string when building dict keys or JSON payloads.

    TS 28.552 §5 (PM counters):
        https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/28552-i50.zip
    """

    # --- DRB — Data Radio Bearer (TS 28.552) ---------------------------------
    DRB_PRB_UTIL_DL = "DRB.PrbUtilDL"  # §5.1.1.12.1, Table 5.1.1.12.1-1, p.47
    DRB_PRB_UTIL_UL = "DRB.PrbUtilUL"  # §5.1.1.12.2, Table 5.1.1.12.2-1, p.48
    DRB_UE_THP_DL = "DRB.UEThpDL"  # §5.1.1.10.1, Table 5.1.1.10.1-1, p.44  (kbps)
    DRB_UE_THP_UL = "DRB.UEThpUL"  # §5.1.1.10.2, Table 5.1.1.10.2-1, p.45  (kbps)

    # --- RRC — Radio Resource Control (TS 28.552) ----------------------------
    RRC_CONN_MEAN = "RRC.ConnMean"  # §5.1.1.1.1, Table 5.1.1.1.1-1, p.21
    RRC_CONN_MAX = "RRC.ConnMax"  # §5.1.1.1.2, Table 5.1.1.1.2-1, p.22

    # --- Radio measurements (TS 36.214 §5) -----------------------------------
    RSRP = "RSRP"  # §5.1.1, p.9  — Reference Signal Received Power (dBm)
    RSRQ = "RSRQ"  # §5.1.2, p.10 — Reference Signal Received Quality (dB)
    SINR = "SINR"  # §5.1.4, p.12 — Signal-to-Interference-plus-Noise Ratio (dB)

    # --- PEE — Power, Energy and Environmental (TS 28.552 §5.1.1.19) ---------
    PEE_AVG_POWER = "PEE.AvgPower"  # §5.1.1.19.2.1, p.64 — mean PNF power (W)
    PEE_ENERGY = "PEE.Energy"  # §5.1.1.19.3, p.65 — PNF energy consumed (kWh)

    # --- O1 VES events (TS 28.532) -------------------------------------------
    CELL_STATUS = "cellStatusChange"  # §5.2.6.2, p.28
