"""Tests for the IBN intent contract validation (whitelist, expiry, HMAC)."""

from __future__ import annotations

import time
from dataclasses import replace

import pytest

from models.intent import (
    IntentContract,
    IntentResolutionService,
    IntentType,
    IntentValidationError,
)


def test_valid_contract_passes(signed_contract: IntentContract, intent_secret: str) -> None:
    svc = IntentResolutionService(secret_key=intent_secret)
    assert svc.validate(signed_contract) is True


def test_expired_contract_rejected(signed_contract: IntentContract, intent_secret: str) -> None:
    svc = IntentResolutionService(secret_key=intent_secret)
    expired = replace(signed_contract, expires_at=time.time() - 1)
    with pytest.raises(IntentValidationError, match="expired"):
        svc.validate(expired)


def test_tampered_signature_rejected(signed_contract: IntentContract, intent_secret: str) -> None:
    svc = IntentResolutionService(secret_key=intent_secret)
    # Changing issued_by invalidates the HMAC over the canonical payload.
    tampered = replace(signed_contract, issued_by="attacker")
    with pytest.raises(IntentValidationError, match="Signature"):
        svc.validate(tampered)


def test_wrong_secret_rejected(signed_contract: IntentContract) -> None:
    svc = IntentResolutionService(secret_key="not-the-real-secret")
    with pytest.raises(IntentValidationError, match="Signature"):
        svc.validate(signed_contract)


def test_resolve_is_not_yet_implemented(
    signed_contract: IntentContract, intent_secret: str
) -> None:
    svc = IntentResolutionService(secret_key=intent_secret)
    with pytest.raises(NotImplementedError):
        svc.resolve(signed_contract, kpis=object())


def test_intent_type_whitelist_membership() -> None:
    assert "energy_saving" in {t.value for t in IntentType}
    assert "delete_everything" not in {t.value for t in IntentType}
