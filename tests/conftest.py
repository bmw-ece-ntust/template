"""Shared pytest fixtures and helpers for the rApp template test suite.

The ``pythonpath = ["src"]`` setting in ``pyproject.toml`` puts the ``models``,
``controllers``, ``handlers``, ``factories``, ``views``, and ``config`` packages
on the import path, so tests import them exactly as application code does
(``from models import KpiReport``).
"""

from __future__ import annotations

import hashlib
import hmac
import time

import pytest

from factories.telemetry_collector import TelemetryCollector
from models.intent import IntentConstraint, IntentContract, IntentType


class FakeTelemetryCollector(TelemetryCollector):
    """In-memory test double returning a fixed raw-telemetry dict.

    Replaces the removed ``mock`` platform for unit tests: pair it with any
    pure analyzer (e.g. :class:`factories.osc.OscKpiAnalyzer` for 3GPP names
    or a vendor analyzer for proprietary names) to drive a full
    :class:`controllers.kpi_controller.KpiController` cycle without network.

    :param fixture: ``{counter_name: value}`` dict returned by :meth:`collect`.
    """

    def __init__(self, fixture: dict[str, float]) -> None:
        self._fixture = fixture

    def collect(self) -> dict[str, float]:
        """Return the canned fixture unchanged.

        :return: The fixture dict passed at construction.
        """
        return dict(self._fixture)


def _sign(secret: str, contract_fields: dict[str, object]) -> str:
    """Reproduce IntentResolutionService canonical HMAC over contract fields."""
    payload = (
        f"{contract_fields['intent_id']}:{contract_fields['intent_type']}"
        f":{contract_fields['issued_by']}:{contract_fields['issued_at']}"
        f":{contract_fields['expires_at']}"
    ).encode()
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


@pytest.fixture
def intent_secret() -> str:
    """A throwaway HMAC secret for intent-contract tests."""
    return "unit-test-secret"


@pytest.fixture
def signed_contract(intent_secret: str) -> IntentContract:
    """A valid, correctly signed, non-expired energy-saving intent contract."""
    fields: dict[str, object] = {
        "intent_id": "intent-001",
        "intent_type": IntentType.ENERGY_SAVING,
        "issued_by": "smo-operator",
        "issued_at": time.time(),
        "expires_at": time.time() + 3600,
    }
    signature = _sign(intent_secret, fields)
    return IntentContract(
        intent_id="intent-001",
        intent_type=IntentType.ENERGY_SAVING,
        objective="Keep DL PRB below 80%",
        constraints=(IntentConstraint("DRB.PrbUtilDL", "lte", 0.8),),
        signature=signature,
        issued_by="smo-operator",
        issued_at=fields["issued_at"],  # type: ignore[arg-type]
        expires_at=fields["expires_at"],  # type: ignore[arg-type]
    )
