"""Tests for KpiReport and its 3GPP bridge."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from models import KpiReport, PolicyDecision
from models.parameters import NodeType, ThreeGPPKpi


def test_kpi_report_defaults() -> None:
    report = KpiReport(cell_id="cell-0")
    assert report.gnb_id == ""
    assert report.node_type is NodeType.GNB
    assert report.rsrp_dbm is None


def test_kpi_report_is_frozen() -> None:
    report = KpiReport(cell_id="cell-0")
    with pytest.raises(FrozenInstanceError):
        report.cell_id = "mutated"  # type: ignore[misc]


def test_from_3gpp_maps_fields_and_coerces_ue_count() -> None:
    report = KpiReport.from_3gpp(
        "cell-1",
        {
            ThreeGPPKpi.DRB_PRB_UTIL_DL: 0.55,
            ThreeGPPKpi.RRC_CONN_MEAN: 12.0,
            ThreeGPPKpi.RSRP: -95.0,
        },
        gnb_id="gnb-1",
        node_type=NodeType.GNB,
    )
    assert report.prb_util_dl == 0.55
    assert report.active_ue_count == 12
    assert isinstance(report.active_ue_count, int)
    assert report.rsrp_dbm == -95.0
    assert report.gnb_id == "gnb-1"


def test_from_3gpp_ignores_unmapped_keys() -> None:
    # CELL_STATUS has no KpiReport field; it must be silently ignored.
    report = KpiReport.from_3gpp("cell-2", {ThreeGPPKpi.CELL_STATUS: 1.0})
    assert report == KpiReport(cell_id="cell-2")


def test_policy_decision_values() -> None:
    assert {d.value for d in PolicyDecision} == {"active", "sleep", "handover"}
