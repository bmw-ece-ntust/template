"""Tests for the per-vendor platform factories (Abstract Factory + Adapter).

Each vendor factory's ``KpiAnalyzer`` encapsulates the Adapter translation from
proprietary PM counter names to 3GPP ``KpiReport`` fields.  These tests drive
the analyzer directly with raw proprietary dicts (no network), and confirm the
composition root resolves the right factory by ``RAPP_PLATFORM``.
"""

from __future__ import annotations

import pytest

from config.settings import Settings
from factories.ericsson import EricssonParam, EricssonPlatformFactory
from factories.nokia import NokiaParam, NokiaPlatformFactory
from main import _build_factory


def test_ericsson_analyzer_maps_proprietary_to_kpi_report() -> None:
    analyzer = EricssonPlatformFactory("http://enm", "cell-1", gnb_id="gnb-er").create_kpi_analyzer()
    report = analyzer.analyze(
        {
            EricssonParam.PRB_USAGE_DL_PCT.value: 42.0,
            EricssonParam.RRC_CONN_AVG.value: 12.0,
            EricssonParam.RSRP_DBM.value: -95.0,
        }
    )
    assert report.prb_util_dl == 42.0
    assert report.active_ue_count == 12
    assert report.rsrp_dbm == -95.0
    assert report.gnb_id == "gnb-er"


def test_nokia_analyzer_maps_proprietary_to_kpi_report() -> None:
    analyzer = NokiaPlatformFactory("http://netact", "cell-2").create_kpi_analyzer()
    report = analyzer.analyze({"NR_PrbUsedDlPct": 30.0, "NR_RsrqMeanDb": -9.0})
    assert report.prb_util_dl == 30.0
    assert report.rsrq_db == -9.0


def test_partial_telemetry_is_tolerated() -> None:
    # Only one metric available; the rest are missing and must default to zero.
    analyzer = EricssonPlatformFactory("http://enm", "cell-3").create_kpi_analyzer()
    report = analyzer.analyze({EricssonParam.PRB_USAGE_DL_PCT.value: 10.0})
    assert report.prb_util_dl == 10.0
    assert report.active_ue_count == 0


def test_unmapped_proprietary_keys_are_ignored() -> None:
    analyzer = NokiaPlatformFactory("http://netact", "cell-4").create_kpi_analyzer()
    report = analyzer.analyze({"NR_PrbUsedDlPct": 55.0, "NR_SomethingUnknown": 1.0})
    assert report.prb_util_dl == 55.0


def test_build_factory_resolves_vendor_by_platform() -> None:
    eric = _build_factory(Settings(platform="ericsson", cell_id="c"))
    nok = _build_factory(Settings(platform="nokia", cell_id="c"))
    assert isinstance(eric, EricssonPlatformFactory)
    assert isinstance(nok, NokiaPlatformFactory)


def test_build_factory_unknown_platform_raises() -> None:
    with pytest.raises(ValueError, match="Unknown RAPP_PLATFORM"):
        _build_factory(Settings(platform="huawei"))
