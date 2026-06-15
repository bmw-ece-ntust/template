"""Normalize proprietary Ericsson telemetry into a standard 3GPP KpiReport.

Shows the Adapter pattern: a vendor-specific client returning proprietary
counter names is wrapped by EricssonTelemetryAdapter, which maps them to
spec-traceable ThreeGPPKpi fields. The same rApp core logic then consumes the
resulting KpiReport regardless of vendor.

Run::

    PYTHONPATH=src python -m examples.vendor_ericsson_adapter
"""

from __future__ import annotations

from typing import ClassVar

from handlers.adapters import get_vendor_adapter
from handlers.adapters.ericsson import EricssonParam
from handlers.vendor import VendorTelemetryClient
from models import KpiReport


class FakeEricssonClient(VendorTelemetryClient):
    """Stand-in for a real Ericsson PM client (returns canned proprietary values)."""

    _DATA: ClassVar[dict[str, float]] = {
        EricssonParam.PRB_USAGE_DL_PCT.value: 63.0,
        EricssonParam.PRB_USAGE_UL_PCT.value: 41.0,
        EricssonParam.RRC_CONN_AVG.value: 18.0,
        EricssonParam.RSRP_DBM.value: -92.0,
        EricssonParam.SINR_DB.value: 21.0,
    }

    def get_metric(self, metric_name: str) -> float:
        return self._DATA[metric_name]


def run() -> KpiReport:
    """Resolve the Ericsson adapter and return a normalized KpiReport."""
    adapter = get_vendor_adapter("ericsson", FakeEricssonClient())
    report = adapter.to_kpi_report("o-du-2222/cell-3", gnb_id="gnb-er-1")
    print(f"normalized report: {report}")
    return report


if __name__ == "__main__":
    run()
