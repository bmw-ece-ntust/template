"""Signed intent contract for contract-based IBN (IETF RFC 9315)."""

from __future__ import annotations

from dataclasses import dataclass

from models.intent.intent_constraint import IntentConstraint
from models.intent.intent_type import IntentType


@dataclass(frozen=True)
class IntentContract:
    """Signed intent contract for contract-based IBN.

    The signature field carries an HMAC-SHA256 digest of the contract's
    canonical JSON representation (all fields except ``signature`` itself),
    keyed with the secret provisioned at SME registration.

    :param intent_id: Unique contract identifier (UUID v4 recommended).
    :param intent_type: One of the :class:`~models.intent.IntentType`
        whitelist values.
    :param objective: Human-readable goal (e.g. ``"Keep DL PRB below 80%"``).
    :param constraints: Tuple of :class:`~models.intent.IntentConstraint`
        conditions.
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
