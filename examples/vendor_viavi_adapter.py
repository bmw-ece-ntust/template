"""Normalize VIAVI RIC Test telemetry into a standard 3GPP KpiReport.

Shows the single-axis multi-vendor design: ``RAPP_PLATFORM=viavi`` selects
the VIAVI Abstract Factory, whose KpiAnalyzer encapsulates the Adapter that
maps VIAVI KPI names to spec-traceable ThreeGPPKpi fields.  The same rApp
core logic then consumes the resulting KpiReport regardless of vendor —
swap ``viavi`` for ``ns3``, ``oai``, or ``ocudu`` and nothing else changes.

Note how ``Viavi.QoS.Score`` (no 3GPP equivalent) is silently dropped, and
how the PEE energy counters flow into ``avg_power_w`` / ``energy_kwh`` for
the energy-saving use case.

Run::

    PYTHONPATH=src python -m examples.vendor_viavi_adapter
"""

from __future__ import annotations

from controllers.strategies import EnergySavingStrategy
from factories.viavi import ViaviKpiAnalyzer, ViaviParam
from models import KpiReport

#: Canned VIAVI values standing in for a live ICS delivery from RIC Test.
_FAKE_VIAVI_RESULT: dict[str, float] = {
    ViaviParam.PRB_USED_DL.value: 0.06,
    ViaviParam.PRB_USED_UL.value: 0.03,
    ViaviParam.RRC_CONN_MEAN.value: 1.0,
    ViaviParam.AVG_POWER_W.value: 410.0,
    ViaviParam.ENERGY_KWH.value: 2.1,
    ViaviParam.QOS_SCORE.value: 91.0,  # proprietary extra — dropped by the map
}


def run() -> KpiReport:
    """Normalize a raw VIAVI dict and feed it to the energy-saving strategy."""
    # In production, ViaviPlatformFactory.create_kpi_analyzer() builds this
    # and its collector fetches _FAKE_VIAVI_RESULT via the R1/ICS interface.
    analyzer = ViaviKpiAnalyzer("S1/B2/C1", gnb_id="gnb-viavi-1")
    report = analyzer.analyze(_FAKE_VIAVI_RESULT)

    decision = EnergySavingStrategy().evaluate(report)

    print(f"normalized report: {report}")
    print(f"avg_power={report.avg_power_w:.0f} W -> decision: {decision.value}")
    return report


if __name__ == "__main__":
    run()
