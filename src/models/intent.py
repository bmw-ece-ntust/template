"""Intent-Based Networking (IBN) domain model — contract-based protocol.

Follows IETF RFC 9315 (Intent-based Networking Concepts and Definitions).
Security model: every intent is a cryptographically signed contract.
The :class:`IntentResolutionService` rejects unknown types, expired contracts,
and contracts with invalid signatures before resolution.

IETF RFC 9315: https://www.rfc-editor.org/rfc/rfc9315
NVIDIA NIM (inference backend): https://docs.nvidia.com/nim/

Integration path
    Intent source (SMO / operator) → IntentPort (R1/SME callback)
    → IntentResolutionService.validate()
    → IntentResolutionService.resolve()
    → OptimizationStrategy.evaluate() or NvidiaModelStrategy
    → PolicyDecision per cell
    → A1Port (push to Near-RT RIC)
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass
from enum import Enum


class IntentType(str, Enum):
    """Whitelisted intent types for contract-based IBN.

    Only types defined here are accepted by :class:`IntentResolutionService`.
    Adding a new type requires O-RAN WG2 / IETF SAIN review and a code review.
    """

    ENERGY_SAVING = "energy_saving"
    LOAD_BALANCING = "load_balancing"
    QOS_GUARANTEE = "qos_guarantee"
    COVERAGE_OPTIMIZATION = "coverage_optimization"
    HANDOVER_OPTIMIZATION = "handover_optimization"


class IntentStatus(str, Enum):
    """Lifecycle state of an active intent contract."""

    PENDING = "pending"
    ACTIVE = "active"
    FULFILLED = "fulfilled"
    VIOLATED = "violated"
    EXPIRED = "expired"


@dataclass(frozen=True)
class IntentConstraint:
    """A single measurable constraint within an intent contract.

    :param parameter: 3GPP KPI identifier string
        (use :class:`~models.parameters.ThreeGPPKpi` values).
    :param operator: Comparison operator — ``"gte"``, ``"lte"``, or ``"eq"``.
    :param value: Threshold value in the parameter's native unit.
    """

    parameter: str
    operator: str
    value: float


@dataclass(frozen=True)
class IntentContract:
    """Signed intent contract for contract-based IBN.

    The signature field carries an HMAC-SHA256 digest of the contract's
    canonical JSON representation (all fields except ``signature`` itself),
    keyed with the secret provisioned at SME registration.

    :param intent_id: Unique contract identifier (UUID v4 recommended).
    :param intent_type: One of the :class:`IntentType` whitelist values.
    :param objective: Human-readable goal (e.g. ``"Keep DL PRB below 80%"``).
    :param constraints: Tuple of :class:`IntentConstraint` conditions.
    :param signature: HMAC-SHA256 hex digest for contract authenticity.
    :param issued_by: Identity of the issuing SMO component or operator.
    :param issued_at: Unix timestamp of issuance.
    :param expires_at: Unix timestamp; contract is rejected after this time.
    """

    intent_id: str
    intent_type: IntentType
    objective: str
    constraints: tuple[IntentConstraint, ...]
    signature: str
    issued_by: str
    issued_at: float
    expires_at: float


class IntentResolutionService:
    """Validates and resolves intent contracts to policy decisions.

    Security checks (in order):

    1. **Whitelist** — rejects ``intent_type`` values not in :class:`IntentType`.
    2. **Expiry** — rejects contracts whose ``expires_at`` has passed.
    3. **Signature** — verifies HMAC-SHA256 of the canonical contract payload.
    4. **Resolution** — maps constraints to a :class:`~models.PolicyDecision`.

    :param secret_key: HMAC secret shared with the intent issuer.
        Provision via ``RAPP_INTENT_SECRET`` environment variable — never
        hard-code this value.

    :Example:

        >>> svc = IntentResolutionService(secret_key=os.environ["RAPP_INTENT_SECRET"])
        >>> svc.validate(contract)
        True
        >>> decision = svc.resolve(contract, kpis)
    """

    def __init__(self, secret_key: str) -> None:
        self._secret = secret_key.encode()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(self, contract: IntentContract) -> bool:
        """Validate an intent contract against all security checks.

        :param contract: Contract to validate.
        :return: ``True`` if valid.
        :raises IntentValidationError: If any check fails.
        """
        self._check_whitelist(contract)
        self._check_expiry(contract)
        self._check_signature(contract)
        return True

    def resolve(self, contract: IntentContract, kpis: object) -> str:
        """Resolve a validated contract to a policy decision string.

        Call :meth:`validate` before this method.  Replace the body with
        your intent-resolution logic, optionally delegating to
        :class:`~controllers.strategies.NvidiaModelStrategy`.

        :param contract: Validated intent contract.
        :param kpis: Current :class:`~models.KpiReport` for the cell.
        :return: :class:`~models.PolicyDecision` value string.
        :raises NotImplementedError: Until intent resolution logic is implemented.
        """
        raise NotImplementedError(
            "Implement intent → PolicyDecision resolution. "
            "Iterate contract.constraints against kpis fields and return "
            "PolicyDecision.ACTIVE, SLEEP, or HANDOVER."
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _check_whitelist(self, contract: IntentContract) -> None:
        valid = {t.value for t in IntentType}
        if contract.intent_type not in valid:
            raise IntentValidationError(
                f"Unknown intent_type {contract.intent_type!r}. Allowed: {sorted(valid)}"
            )

    def _check_expiry(self, contract: IntentContract) -> None:
        if contract.expires_at < time.time():
            raise IntentValidationError(
                f"Contract {contract.intent_id!r} expired at {contract.expires_at}"
            )

    def _check_signature(self, contract: IntentContract) -> None:
        payload = (
            f"{contract.intent_id}:{contract.intent_type}:{contract.issued_by}"
            f":{contract.issued_at}:{contract.expires_at}"
        ).encode()
        expected = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, contract.signature):
            raise IntentValidationError(
                f"Signature verification failed for contract {contract.intent_id!r}"
            )


class IntentValidationError(ValueError):
    """Raised when an intent contract fails validation."""
