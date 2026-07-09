"""Validation and resolution of signed intent contracts."""

from __future__ import annotations

import hashlib
import hmac
import time

from models.intent.intent_contract import IntentContract
from models.intent.intent_type import IntentType
from models.intent.intent_validation_error import IntentValidationError


class IntentResolutionService:
    """Validates and resolves intent contracts to policy decisions.

    Security checks (in order):

    1. **Whitelist** — rejects ``intent_type`` values not in
       :class:`~models.intent.IntentType`.
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
