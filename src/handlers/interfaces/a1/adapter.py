"""A1 policy instance management via the Non-RT RIC A1 mediator."""

from __future__ import annotations

import logging
from typing import Any

import requests

from handlers.interfaces.a1.error import A1Error
from models import PolicyDecision

_log = logging.getLogger(__name__)

#: Maps a :class:`~models.PolicyDecision` to the A1 traffic-steering
#: ``preference`` value defined in ``ORAN_TrafficSteering_0.1.0``.
_PREFERENCE_MAP: dict[PolicyDecision, str] = {
    PolicyDecision.ACTIVE: "PREFER",
    PolicyDecision.SLEEP: "AVOID",
    PolicyDecision.HANDOVER: "FORBID",
}


class A1Adapter:
    """Creates and manages A1 policy instances via the Non-RT RIC A1 mediator.

    The adapter translates a :class:`~models.PolicyDecision` into the
    ``ORAN_TrafficSteering_0.1.0`` policy schema and pushes it to the target
    Near-RT RIC through the Non-RT RIC A1 Policy Management Service.

    :param a1_base_url: Base URL of the A1 Policy Management Service
        (e.g. ``http://a1policymanagementservice.nonrtric.svc:8081``).
    :param policy_type_id: A1 policy type to manage.
                            Defaults to ``"ORAN_TrafficSteering_0.1.0"``.

    :Example:

        >>> a1 = A1Adapter("http://a1policymanagementservice.nonrtric.svc:8081")
        >>> policy_id = a1.create_policy(
        ...     near_rt_ric_id="near-rt-ric-1",
        ...     cell_id="cell-001",
        ...     decision=PolicyDecision.SLEEP,
        ... )
        >>> status = a1.get_policy_status(policy_id)
        >>> a1.delete_policy(policy_id)

    .. note::

        The ``ORAN_TrafficSteering_0.1.0`` schema is defined in the O-RAN SC
        A1 Policy Management Service integration tests.  Query
        ``GET /a1-policy/v2/policy-types/{policy_type_id}`` against the
        A1PMS to retrieve the live JSON Schema for your deployment.
    """

    _POLICY_PATH = "/a1-policy/v2/policies"

    def __init__(
        self,
        a1_base_url: str,
        policy_type_id: str = "ORAN_TrafficSteering_0.1.0",
    ) -> None:
        self._base = a1_base_url.rstrip("/")
        self.policy_type_id = policy_type_id
        self._session = requests.Session()
        self._session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    # --- A1Port implementation ----------------------------------------------

    def create_policy(
        self,
        near_rt_ric_id: str,
        cell_id: str,
        decision: PolicyDecision,
        policy_id: str | None = None,
    ) -> str:
        """Create or update an A1 policy instance for a cell.

        If *policy_id* is ``None``, an ID is auto-generated from the policy
        type and cell identifier.  Calling this method again with the same
        *policy_id* performs an idempotent update (HTTP PUT).

        :param near_rt_ric_id: Target Near-RT RIC identifier.
        :param cell_id: NR Cell Global ID for which the policy applies.
        :param decision: Policy decision from the optimization strategy.
        :param policy_id: Explicit policy ID; auto-generated if ``None``.
        :return: The created or updated policy ID.
        :raises A1Error: If the policy is rejected by the A1 Policy Management Service.
        """
        if policy_id is None:
            policy_id = f"{self.policy_type_id}-{cell_id}"
        url = f"{self._base}{self._POLICY_PATH}/{policy_id}"
        body: dict[str, Any] = {
            "policyId": policy_id,
            "policyTypeId": self.policy_type_id,
            "nearRtRicId": near_rt_ric_id,
            "policyData": self._decision_to_policy_data(cell_id, decision),
        }
        _log.info(
            "A1 create_policy  policy_id=%s  cell=%s  decision=%s",
            policy_id,
            cell_id,
            decision.value,
        )
        try:
            resp = self._session.put(url, json=body, timeout=10)
            resp.raise_for_status()
            return policy_id
        except requests.RequestException as exc:
            raise A1Error(f"A1 create_policy({policy_id!r}) failed: {exc}") from exc

    def delete_policy(self, policy_id: str) -> None:
        """Delete an A1 policy instance.

        :param policy_id: Policy ID returned by :meth:`create_policy`.
        :raises A1Error: If deletion fails.
        """
        url = f"{self._base}{self._POLICY_PATH}/{policy_id}"
        _log.info("A1 delete_policy  policy_id=%s", policy_id)
        try:
            resp = self._session.delete(url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise A1Error(f"A1 delete_policy({policy_id!r}) failed: {exc}") from exc

    def get_policy_status(self, policy_id: str) -> dict[str, Any]:
        """Query the enforcement status of a policy instance.

        :param policy_id: Policy ID.
        :return: Status object from the Near-RT RIC (enforcement state, etc.).
        :raises A1Error: On HTTP error.
        """
        url = f"{self._base}{self._POLICY_PATH}/{policy_id}/status"
        try:
            resp = self._session.get(url, timeout=10)
            resp.raise_for_status()
            status: dict[str, Any] = resp.json()
            return status
        except requests.RequestException as exc:
            raise A1Error(f"A1 get_policy_status({policy_id!r}) failed: {exc}") from exc

    # --- Adapter mapping: PolicyDecision → A1 policy schema ----------------

    @staticmethod
    def _decision_to_policy_data(cell_id: str, decision: PolicyDecision) -> dict[str, Any]:
        """Map a :class:`~models.PolicyDecision` to ``ORAN_TrafficSteering_0.1.0`` data.

        .. list-table:: Decision mapping
           :header-rows: 1

           * - PolicyDecision
             - A1 preference
             - Behaviour
           * - ``ACTIVE``
             - ``PREFER``
             - Near-RT RIC prefers this cell for traffic
           * - ``SLEEP``
             - ``AVOID``
             - Near-RT RIC avoids this cell (energy saving)
           * - ``HANDOVER``
             - ``FORBID``
             - Near-RT RIC forbids new admissions; triggers handover

        :param cell_id: NR Cell Global ID.
        :param decision: Optimization policy decision.
        :return: A1 policy data dictionary conforming to ``ORAN_TrafficSteering_0.1.0``.
        """
        return {
            "scope": {"qosId": "default", "ueId": cell_id},
            "resources": [
                {
                    "cellIdList": [cell_id],
                    "preference": _PREFERENCE_MAP[decision],
                }
            ],
        }
