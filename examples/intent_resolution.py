"""Build and validate a signed IBN intent contract (RFC 9315 style).

Shows the security contract every intent must pass before resolution:
whitelist → expiry → HMAC signature. Resolution itself is intentionally a
stub in the template (implement per use case).

Run::

    PYTHONPATH=src python -m examples.intent_resolution
"""

from __future__ import annotations

import hashlib
import hmac
import time

from models.intent import (
    IntentConstraint,
    IntentContract,
    IntentResolutionService,
    IntentType,
)

SECRET = "demo-shared-secret"  # provision via RAPP_INTENT_SECRET in production


def _sign(
    intent_id: str, intent_type: IntentType, issued_by: str, issued_at: float, expires_at: float
) -> str:
    payload = f"{intent_id}:{intent_type}:{issued_by}:{issued_at}:{expires_at}".encode()
    return hmac.new(SECRET.encode(), payload, hashlib.sha256).hexdigest()


def run() -> bool:
    """Construct a signed energy-saving intent and validate it."""
    issued_at = time.time()
    expires_at = issued_at + 3600
    signature = _sign("intent-001", IntentType.ENERGY_SAVING, "smo-operator", issued_at, expires_at)

    contract = IntentContract(
        intent_id="intent-001",
        intent_type=IntentType.ENERGY_SAVING,
        objective="Keep DL PRB utilization below 80%",
        constraints=(IntentConstraint("DRB.PrbUtilDL", "lte", 0.8),),
        signature=signature,
        issued_by="smo-operator",
        issued_at=issued_at,
        expires_at=expires_at,
    )

    service = IntentResolutionService(secret_key=SECRET)
    valid = service.validate(contract)
    print(f"intent {contract.intent_id} valid={valid} type={contract.intent_type.value}")
    return valid


if __name__ == "__main__":
    run()
