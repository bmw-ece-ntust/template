"""Normalize proprietary Ericsson telemetry into a standard 3GPP KpiReport.

Shows the single-axis design: ``RAPP_PLATFORM=ericsson`` selects the Ericsson
Abstract Factory, whose KpiAnalyzer encapsulates the Adapter that maps
proprietary counter names to spec-traceable ThreeGPPKpi fields. The same rApp
core logic then consumes the resulting KpiReport regardless of vendor.

Run::

    PYTHONPATH=src python -m examples.vendor_ericsson_adapter
"""

from __future__ import annotations

from factories.ericsson import EricssonParam, EricssonPlatformFactory
from models import KpiReport

#: Canned proprietary values standing in for a live Ericsson PM poll.
_FAKE_PM_RESULT: dict[str, float] = {
    EricssonParam.PRB_USAGE_DL_PCT.value: 63.0,
    EricssonParam.PRB_USAGE_UL_PCT.value: 41.0,
    EricssonParam.RRC_CONN_AVG.value: 18.0,
    EricssonParam.RSRP_DBM.value: -92.0,
    EricssonParam.SINR_DB.value: 21.0,
}


def run() -> KpiReport:
    """Build the Ericsson factory and normalize a raw PM dict to a KpiReport."""
    factory = EricssonPlatformFactory(
        ems_base_url="http://enm:8080",
        cell_id="o-du-2222/cell-3",
        gnb_id="gnb-er-1",
    )
    # In production, factory.create_telemetry_collector().collect() fetches this
    # from the Ericsson management plane; here we feed canned values directly.
    report = factory.create_kpi_analyzer().analyze(_FAKE_PM_RESULT)
    print(f"normalized report: {report}")
    return report


if __name__ == "__main__":
    run()
