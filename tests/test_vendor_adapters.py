"""Tests for the multi-vendor proprietary adapters and registry."""

from __future__ import annotations

import pytest

from handlers.adapters import (
    get_vendor_adapter,
    registered_vendors,
)
from handlers.adapters.ericsson import EricssonParam, EricssonTelemetryAdapter
from handlers.adapters.nokia import NokiaTelemetryAdapter
from handlers.vendor import VendorTelemetryClient


class _FakeClient(VendorTelemetryClient):
    """Returns canned values; raises KeyError for unmapped keys (skipped)."""

    def __init__(self, data: dict[str, float]) -> None:
        self._data = data

    def get_metric(self, metric_name: str) -> float:
        return self._data[metric_name]


def test_registry_lists_known_vendors() -> None:
    assert {"ericsson", "nokia"} <= set(registered_vendors())


def test_ericsson_adapter_maps_proprietary_to_kpi_report() -> None:
    client = _FakeClient(
        {
            EricssonParam.PRB_USAGE_DL_PCT.value: 42.0,
            EricssonParam.RRC_CONN_AVG.value: 12.0,
            EricssonParam.RSRP_DBM.value: -95.0,
        }
    )
    report = EricssonTelemetryAdapter(client).to_kpi_report("cell-1", gnb_id="gnb-er")
    assert report.prb_util_dl == 42.0
    assert report.active_ue_count == 12
    assert report.rsrp_dbm == -95.0
    assert report.gnb_id == "gnb-er"


def test_nokia_adapter_maps_proprietary_to_kpi_report() -> None:
    client = _FakeClient({"NR_PrbUsedDlPct": 30.0, "NR_RsrqMeanDb": -9.0})
    report = NokiaTelemetryAdapter(client).to_kpi_report("cell-2")
    assert report.prb_util_dl == 30.0
    assert report.rsrq_db == -9.0


def test_partial_telemetry_is_tolerated() -> None:
    # Only one metric available; the rest are missing and must be skipped.
    client = _FakeClient({EricssonParam.PRB_USAGE_DL_PCT.value: 10.0})
    report = EricssonTelemetryAdapter(client).to_kpi_report("cell-3")
    assert report.prb_util_dl == 10.0
    assert report.active_ue_count == 0


def test_get_vendor_adapter_is_case_insensitive() -> None:
    adapter = get_vendor_adapter("ERICSSON", _FakeClient({}))
    assert isinstance(adapter, EricssonTelemetryAdapter)


def test_get_vendor_adapter_unknown_raises() -> None:
    with pytest.raises(KeyError, match="No vendor adapter"):
        get_vendor_adapter("huawei", _FakeClient({}))
