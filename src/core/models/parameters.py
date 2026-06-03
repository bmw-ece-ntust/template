"""3GPP and O-RAN parameter identifier enumerations.

Using string enumerations eliminates typos, enables IDE auto-completion,
and makes the vendor-to-3GPP parameter mapping explicit and spec-traceable.

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
    DRB_UE_THP_DL   = "DRB.UEThpDL"    # §5.1.1.10.1, Table 5.1.1.10.1-1, p.44  (kbps)
    DRB_UE_THP_UL   = "DRB.UEThpUL"    # §5.1.1.10.2, Table 5.1.1.10.2-1, p.45  (kbps)

    # --- RRC — Radio Resource Control (TS 28.552) ----------------------------
    RRC_CONN_MEAN = "RRC.ConnMean"      # §5.1.1.1.1, Table 5.1.1.1.1-1, p.21
    RRC_CONN_MAX  = "RRC.ConnMax"       # §5.1.1.1.2, Table 5.1.1.1.2-1, p.22

    # --- Radio measurements (TS 36.214 §5) -----------------------------------
    RSRP = "RSRP"   # §5.1.1, p.9  — Reference Signal Received Power (dBm)
    RSRQ = "RSRQ"   # §5.1.2, p.10 — Reference Signal Received Quality (dB)
    SINR = "SINR"   # §5.1.4, p.12 — Signal-to-Interference-plus-Noise Ratio (dB)

    # --- O1 VES events (TS 28.532) -------------------------------------------
    CELL_STATUS = "cellStatusChange"    # §5.2.6.2, p.28


class NodeType(str, Enum):
    """Network node type — selects the correct parameter mapping and adapter.

    :cvar GNB: 5G NR base station cell (gNB-DU / gNB-CU).
    :cvar ENODEB: 4G LTE eNodeB cell.
    :cvar WIFI_AP: IEEE 802.11 access point; mapped to 3GPP KPIs via O1 vendor adapter.
    """

    GNB     = "gnb"
    ENODEB  = "enodeb"
    WIFI_AP = "wifi_ap"


class VendorParameterMap:
    """Maps proprietary vendor metric names to :class:`ThreeGPPKpi` identifiers.

    Declare a class-level ``PARAM_MAP`` in each
    :class:`~rapp.adapters.vendor.VendorTelemetryClient` subclass::

        PARAM_MAP: ClassVar[dict[str, ThreeGPPKpi]] = {
            "dl_prb_usage_pct": ThreeGPPKpi.DRB_PRB_UTIL_DL,
            "ul_prb_usage_pct": ThreeGPPKpi.DRB_PRB_UTIL_UL,
            "active_ue_count":  ThreeGPPKpi.RRC_CONN_MEAN,
        }

    This makes the Adapter pattern's translation table auditable and
    directly traceable to the 3GPP specification.

    :param mapping: ``{vendor_key: ThreeGPPKpi}`` translation table.
    """

    def __init__(self, mapping: dict[str, ThreeGPPKpi]) -> None:
        self._map = mapping

    def translate(self, vendor_key: str) -> ThreeGPPKpi | None:
        """Return the 3GPP KPI identifier for a vendor metric key.

        :param vendor_key: Proprietary metric key.
        :return: Matching :class:`ThreeGPPKpi`, or ``None`` if unmapped.
        """
        return self._map.get(vendor_key)

    def raw_to_standard(self, raw: dict[str, float]) -> dict[ThreeGPPKpi, float]:
        """Translate a raw vendor metric dict to 3GPP-keyed values.

        Unmapped keys are silently dropped.

        :param raw: ``{vendor_key: value}`` dict from the telemetry client.
        :return: ``{ThreeGPPKpi: value}`` for all recognized keys.
        """
        return {self._map[k]: v for k, v in raw.items() if k in self._map}
