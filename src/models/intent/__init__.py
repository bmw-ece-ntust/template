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

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from models.intent import IntentContract, IntentResolutionService``.
"""

from __future__ import annotations

from models.intent.intent_constraint import IntentConstraint
from models.intent.intent_contract import IntentContract
from models.intent.intent_resolution_service import IntentResolutionService
from models.intent.intent_status import IntentStatus
from models.intent.intent_type import IntentType
from models.intent.intent_validation_error import IntentValidationError

__all__ = [
    "IntentConstraint",
    "IntentContract",
    "IntentResolutionService",
    "IntentStatus",
    "IntentType",
    "IntentValidationError",
]
