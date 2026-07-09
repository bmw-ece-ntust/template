"""E2SM-RC adapter — :class:`~models.PolicyDecision` to RIC Control Requests."""

from __future__ import annotations

import logging
from typing import Any, ClassVar

from handlers.interfaces.e2.client import E2Client
from handlers.interfaces.e2.control_ack import E2ControlAck
from handlers.interfaces.e2.control_request import E2ControlRequest
from models import PolicyDecision

_log = logging.getLogger(__name__)


class E2SmRcAdapter:
    """Adapts :class:`~models.PolicyDecision` to E2SM-RC control requests.

    Maps BMW Lab internal policy decisions to the E2SM-RC control action
    identifiers used by the target Near-RT RIC platform.

    :param e2_client: An :class:`~handlers.interfaces.e2.E2Client` implementation.
    :param ran_function_id: RAN function ID assigned to E2SM-RC by the
        Near-RT RIC (obtained from E2 Setup response).
    :param action_id_map: Optional override mapping
        ``{PolicyDecision: action_id}``.  Defaults cover cell activation
        (action 1), sleep (action 2), and handover (action 3).

    :Example:

        >>> adapter = E2SmRcAdapter(e2_client, ran_function_id=3)
        >>> ack = adapter.apply_decision("o-du-1111/cell-0", PolicyDecision.SLEEP)
    """

    _DEFAULT_ACTION_IDS: ClassVar[dict[PolicyDecision, int]] = {
        PolicyDecision.ACTIVE: 1,
        PolicyDecision.SLEEP: 2,
        PolicyDecision.HANDOVER: 3,
    }

    def __init__(
        self,
        e2_client: E2Client,
        ran_function_id: int,
        action_id_map: dict[PolicyDecision, int] | None = None,
    ) -> None:
        self._client = e2_client
        self._ran_function_id = ran_function_id
        self._action_ids = action_id_map or self._DEFAULT_ACTION_IDS

    # --- E2RcPort implementation --------------------------------------------

    def apply_decision(
        self,
        cell_id: str,
        decision: PolicyDecision,
        extra_params: dict[str, Any] | None = None,
    ) -> E2ControlAck:
        """Send an E2SM-RC control request for a policy decision.

        :param cell_id: Target cell NR CGI.
        :param decision: :class:`~models.PolicyDecision` to enforce.
        :param extra_params: Additional E2SM-RC control parameters
            (e.g. ``{"targetCellId": "cell-1"}`` for handover).
        :return: :class:`E2ControlAck` from the E2 node.
        :raises E2Error: If the control is rejected.
        :raises ValueError: If the decision has no mapped action ID.
        """
        action_id = self._action_ids.get(decision)
        if action_id is None:
            raise ValueError(f"No E2SM-RC action ID mapped for {decision!r}")

        request = E2ControlRequest(
            ran_function_id=self._ran_function_id,
            cell_id=cell_id,
            action_id=action_id,
            action_params=extra_params or {},
        )
        _log.info(
            "E2 RC control  cell=%s  decision=%s  action_id=%d",
            cell_id,
            decision.value,
            action_id,
        )
        return self._client.send_control(request)
