"""Tests for the 3GPP parameter enum and the vendor parameter map."""

from __future__ import annotations

from models.parameters import NodeType, ThreeGPPKpi, VendorParameterMap


def test_threegpp_kpi_values_are_canonical_3gpp_names() -> None:
    assert ThreeGPPKpi.DRB_PRB_UTIL_DL.value == "DRB.PrbUtilDL"
    assert ThreeGPPKpi.RRC_CONN_MEAN.value == "RRC.ConnMean"
    # str-Enum: members compare equal to their string value.
    assert ThreeGPPKpi.RSRP == "RSRP"


def test_node_type_members() -> None:
    assert {n.value for n in NodeType} == {"gnb", "enodeb", "wifi_ap"}


def test_vendor_map_translate_and_keys() -> None:
    vmap = VendorParameterMap(
        {
            "dl_prb_usage_pct": ThreeGPPKpi.DRB_PRB_UTIL_DL,
            "active_ue_count": ThreeGPPKpi.RRC_CONN_MEAN,
        }
    )
    assert vmap.translate("dl_prb_usage_pct") is ThreeGPPKpi.DRB_PRB_UTIL_DL
    assert vmap.translate("unknown_key") is None
    assert set(vmap.keys()) == {"dl_prb_usage_pct", "active_ue_count"}


def test_vendor_map_raw_to_standard_drops_unmapped() -> None:
    vmap = VendorParameterMap({"dl_prb_usage_pct": ThreeGPPKpi.DRB_PRB_UTIL_DL})
    out = vmap.raw_to_standard({"dl_prb_usage_pct": 0.42, "noise": 99.0})
    assert out == {ThreeGPPKpi.DRB_PRB_UTIL_DL: 0.42}
