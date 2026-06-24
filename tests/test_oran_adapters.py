"""Tests for O-RAN standard interface adapters (A1 mapping, E2 KPM/RC)."""

from __future__ import annotations

import json

import pytest

from handlers.interfaces.a1 import A1Adapter
from handlers.interfaces.e2 import (
    E2Client,
    E2ControlAck,
    E2ControlRequest,
    E2Indication,
    E2SmKpmAdapter,
    E2SmRcAdapter,
)
from models import PolicyDecision


class _FakeE2Client(E2Client):
    """In-memory E2 client capturing the last control request."""

    def __init__(self) -> None:
        self.last_request: E2ControlRequest | None = None

    def subscribe_kpm(self, ran_function_id, cell_id, report_interval_ms=1000):  # type: ignore[no-untyped-def]
        return "sub-1"

    def unsubscribe_kpm(self, subscription_id):  # type: ignore[no-untyped-def]
        return None

    def send_control(self, request: E2ControlRequest) -> E2ControlAck:
        self.last_request = request
        return E2ControlAck(success=True, message="accepted")

    def register_indication_handler(self, handler):  # type: ignore[no-untyped-def]
        return None


@pytest.mark.parametrize(
    ("decision", "expected"),
    [
        (PolicyDecision.ACTIVE, "PREFER"),
        (PolicyDecision.SLEEP, "AVOID"),
        (PolicyDecision.HANDOVER, "FORBID"),
    ],
)
def test_a1_decision_maps_to_preference(decision: PolicyDecision, expected: str) -> None:
    payload = A1Adapter._decision_to_policy_data("cell-0", decision)
    assert expected in json.dumps(payload)


def test_e2_rc_apply_decision_sends_mapped_action_id() -> None:
    client = _FakeE2Client()
    adapter = E2SmRcAdapter(client, ran_function_id=3)
    ack = adapter.apply_decision("cell-0", PolicyDecision.SLEEP)
    assert ack.success is True
    assert client.last_request is not None
    assert client.last_request.action_id == 2  # SLEEP → action 2


def test_e2_rc_unmapped_decision_raises() -> None:
    client = _FakeE2Client()
    adapter = E2SmRcAdapter(client, ran_function_id=3, action_id_map={PolicyDecision.ACTIVE: 1})
    with pytest.raises(ValueError, match="action ID"):
        adapter.apply_decision("cell-0", PolicyDecision.SLEEP)


def test_e2_kpm_indication_to_kpi_report() -> None:
    adapter = E2SmKpmAdapter(_FakeE2Client(), ran_function_id=2)
    indication = E2Indication(
        subscription_id="sub-1",
        ran_function_id=2,
        cell_id="cell-7",
        gnb_id="gnb-7",
        pm_counters={"DRB.PrbUtilDL": 0.6, "RRC.ConnMean": 9},
    )
    report = adapter.indication_to_kpi_report(indication)
    assert report.cell_id == "cell-7"
    assert report.prb_util_dl == 0.6
    assert report.active_ue_count == 9
