"""Tests for the per-vendor platform factories (Abstract Factory + Adapter).

Each vendor factory's ``KpiAnalyzer`` encapsulates the Adapter translation
from vendor KPI names (and units) to 3GPP ``KpiReport`` fields.  These tests
drive the analyzers directly with raw vendor dicts (no network), and confirm
the composition root resolves the right factory by ``RAPP_PLATFORM``.
"""

from __future__ import annotations

import pytest

from config.settings import Settings
from factories.ns3 import Ns3KpiAnalyzer, Ns3Param, Ns3PlatformFactory
from factories.oai import OaiKpiAnalyzer, OaiParam, OaiPlatformFactory
from factories.ocudu import OcuduKpiAnalyzer, OcuduParam, OcuduPlatformFactory
from factories.osc import OscPlatformFactory
from factories.viavi import ViaviKpiAnalyzer, ViaviParam, ViaviPlatformFactory
from main import _build_factory


def test_viavi_analyzer_maps_vendor_names_to_kpi_report() -> None:
    analyzer = ViaviKpiAnalyzer("cell-1", gnb_id="gnb-v")
    report = analyzer.analyze(
        {
            ViaviParam.PRB_USED_DL.value: 0.42,
            ViaviParam.RRC_CONN_MEAN.value: 12.0,
            ViaviParam.AVG_POWER_W.value: 380.0,
            ViaviParam.ENERGY_KWH.value: 1.9,
        }
    )
    assert report.prb_util_dl == 0.42
    assert report.active_ue_count == 12
    assert report.avg_power_w == 380.0
    assert report.energy_kwh == 1.9
    assert report.gnb_id == "gnb-v"


def test_viavi_proprietary_extras_are_dropped() -> None:
    # Viavi.QoS.Score has no 3GPP equivalent and must never leak into the core.
    report = ViaviKpiAnalyzer("cell-1").analyze(
        {ViaviParam.QOS_SCORE.value: 87.0, ViaviParam.PRB_USED_DL.value: 0.3}
    )
    assert report.prb_util_dl == 0.3
    assert report.active_ue_count == 0


def test_ns3_analyzer_maps_sinr_and_active_ues() -> None:
    report = Ns3KpiAnalyzer("cell-2").analyze(
        {
            Ns3Param.SERVING_SINR.value: 18.5,
            Ns3Param.MEAN_ACTIVE_UE_DL.value: 4.0,
        }
    )
    assert report.sinr_db == 18.5
    assert report.active_ue_count == 4


def test_oai_analyzer_drops_volume_counter() -> None:
    # DRB.PdcpSduVolumeDL is a volume, not a throughput — must be dropped,
    # never misread into a KpiReport field.
    report = OaiKpiAnalyzer("cell-3").analyze(
        {
            OaiParam.PDCP_SDU_VOL_DL.value: 1.0e6,
            OaiParam.THP_DL_KBPS.value: 5000.0,
        }
    )
    assert report.dl_throughput_kbps == 5000.0


def test_ocudu_analyzer_rescales_bps_to_kbps() -> None:
    # The OCUDU Adapter converts units as well as names.
    report = OcuduKpiAnalyzer("cell-4").analyze(
        {
            OcuduParam.DL_BITRATE_BPS.value: 5_000_000.0,
            OcuduParam.PUSCH_SNR_DB.value: 21.0,
        }
    )
    assert report.dl_throughput_kbps == 5000.0
    assert report.sinr_db == 21.0


def test_partial_telemetry_is_tolerated() -> None:
    # Only one metric available; the rest are missing and must default to zero.
    report = ViaviKpiAnalyzer("cell-5").analyze({ViaviParam.PRB_USED_DL.value: 0.1})
    assert report.prb_util_dl == 0.1
    assert report.active_ue_count == 0


@pytest.mark.parametrize(
    ("platform", "factory_class"),
    [
        ("osc", OscPlatformFactory),
        ("ns3", Ns3PlatformFactory),
        ("viavi", ViaviPlatformFactory),
        ("oai", OaiPlatformFactory),
        ("ocudu", OcuduPlatformFactory),
    ],
)
def test_build_factory_resolves_platform(platform: str, factory_class: type) -> None:
    factory = _build_factory(Settings(platform=platform, cell_id="c"))
    assert type(factory) is factory_class


def test_vendor_factory_produces_vendor_analyzer() -> None:
    factory = _build_factory(Settings(platform="viavi", cell_id="c"))
    assert isinstance(factory.create_kpi_analyzer(), ViaviKpiAnalyzer)


def test_build_factory_unknown_platform_raises() -> None:
    with pytest.raises(ValueError, match="Unknown RAPP_PLATFORM"):
        _build_factory(Settings(platform="huawei"))
