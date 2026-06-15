"""E2 interface adapter stubs — SM-KPM and SM-RC.

The E2 interface connects Near-RT RIC xApps to RAN nodes (gNB-DU / gNB-CU).
Two E2 Service Models are used in most RAN optimization xApps:

E2SM-KPM (Key Performance Metrics)
    xApp subscribes to periodic KPM reports from the E2 node.  The Near-RT
    RIC forwards E2 Indication messages containing 3GPP PM counters.

E2SM-RC (RAN Control)
    xApp sends RIC Control Request messages to the E2 node to trigger
    actions: cell activation/deactivation, UE handover, resource control.

Adapter role
    Translates BMW Lab internal types to/from O-RAN E2 ASN.1 message
    structures.

    .. code-block:: none

        [E2 Indication (ASN.1/protobuf)] <── E2SmKpmAdapter ──> [KpiReport]
        [PolicyDecision]                 <── E2SmRcAdapter  ──> [E2 Control (ASN.1)]

Transport note
    Production deployments use RMR (O-RAN SC) or gRPC (FlexRIC) — neither
    uses HTTP.  :class:`E2Client` abstracts the transport so the xApp logic
    is independent of the underlying message bus.

O-RAN references
    E2AP:     O-RAN.WG3.E2AP-v03.01      https://specifications.o-ran.org/
    E2SM-KPM: O-RAN.WG3.E2SM-KPM-v03.00 https://specifications.o-ran.org/
    E2SM-RC:  O-RAN.WG3.E2SM-RC-v01.03  https://specifications.o-ran.org/

OSC xApp-frame-py reference
    https://gerrit.o-ran-sc.org/r/ric-plt/xapp-frame-py
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, ClassVar

from models import KpiReport, PolicyDecision
from models.parameters import ThreeGPPKpi

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class E2Indication:
    """Decoded E2 Indication message from the Near-RT RIC.

    :param subscription_id: ID returned by :meth:`E2Client.subscribe_kpm`.
    :param ran_function_id: RAN function that produced this indication.
    :param cell_id: Source cell NR CGI.
    :param gnb_id: Source gNB identifier.
    :param pm_counters: 3GPP PM counter name → value mapping.
        Keys are :class:`~models.parameters.ThreeGPPKpi` values.
    :param timestamp_ms: Indication timestamp (Unix epoch milliseconds).
    """

    subscription_id: str
    ran_function_id: int
    cell_id: str
    gnb_id: str
    pm_counters: dict[str, float]
    timestamp_ms: int = 0


@dataclass(frozen=True)
class E2ControlRequest:
    """RIC Control Request payload for E2SM-RC.

    :param ran_function_id: RAN function ID for E2SM-RC.
    :param cell_id: Target cell NR CGI.
    :param action_id: E2SM-RC control action identifier.
    :param action_params: Key-value pairs of control parameters.
    """

    ran_function_id: int
    cell_id: str
    action_id: int
    action_params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class E2ControlAck:
    """Acknowledgement from the E2 node for a RIC Control Request.

    :param success: ``True`` if the control was accepted.
    :param message: Human-readable status message from the E2 node.
    """

    success: bool
    message: str = ""


# ---------------------------------------------------------------------------
# Abstract E2 client
# ---------------------------------------------------------------------------


class E2Client(ABC):
    """Abstract E2 client — transport-independent interface.

    Concrete subclasses implement RMR (O-RAN SC) or gRPC (FlexRIC) transport.
    """

    @abstractmethod
    def subscribe_kpm(
        self,
        ran_function_id: int,
        cell_id: str,
        report_interval_ms: int = 1000,
    ) -> str:
        """Subscribe to periodic KPM reports from a cell.

        :param ran_function_id: RAN function ID for E2SM-KPM.
        :param cell_id: Target cell NR CGI.
        :param report_interval_ms: Report granularity period in milliseconds.
        :return: Subscription ID (pass to :meth:`unsubscribe_kpm`).
        :raises E2Error: If the Near-RT RIC rejects the subscription.
        """

    @abstractmethod
    def unsubscribe_kpm(self, subscription_id: str) -> None:
        """Cancel a KPM subscription.

        :param subscription_id: ID returned by :meth:`subscribe_kpm`.
        :raises E2Error: If cancellation fails.
        """

    @abstractmethod
    def send_control(self, request: E2ControlRequest) -> E2ControlAck:
        """Send a RIC Control Request to a cell.

        :param request: :class:`E2ControlRequest` payload.
        :return: :class:`E2ControlAck` from the E2 node.
        :raises E2Error: If the Near-RT RIC rejects or cannot forward the request.
        """

    @abstractmethod
    def register_indication_handler(
        self,
        handler: Callable[[E2Indication], None],
    ) -> None:
        """Register a callback invoked for every incoming E2 Indication.

        :param handler: Callable receiving one :class:`E2Indication` per call.
        """


# ---------------------------------------------------------------------------
# SM-KPM adapter
# ---------------------------------------------------------------------------


class E2SmKpmAdapter:
    """Adapts E2SM-KPM indications to :class:`~models.KpiReport`.

    Decodes the raw PM counter payload from the E2 node and normalises it
    to the BMW Lab :class:`~models.KpiReport` data model.

    :param e2_client: An :class:`E2Client` implementation.
    :param ran_function_id: RAN function ID assigned to E2SM-KPM by the
        Near-RT RIC (typically obtained from E2 Setup response).

    :Example:

        >>> adapter = E2SmKpmAdapter(e2_client, ran_function_id=2)
        >>> sub_id = adapter.subscribe("o-du-1111/cell-0", interval_ms=500)
        >>> # E2 indications are forwarded to the registered handler
    """

    def __init__(self, e2_client: E2Client, ran_function_id: int) -> None:
        self._client = e2_client
        self._ran_function_id = ran_function_id

    # --- E2KpmPort implementation -------------------------------------------

    def subscribe(self, cell_id: str, interval_ms: int = 1000) -> str:
        """Subscribe to KPM reports for a cell.

        :param cell_id: Target cell NR CGI.
        :param interval_ms: Granularity period in milliseconds.
        :return: Subscription ID.
        :raises E2Error: If the subscription is rejected.
        """
        _log.info("E2 KPM subscribe  cell=%s  interval=%d ms", cell_id, interval_ms)
        return self._client.subscribe_kpm(self._ran_function_id, cell_id, interval_ms)

    def unsubscribe(self, subscription_id: str) -> None:
        """Cancel a KPM subscription.

        :param subscription_id: ID returned by :meth:`subscribe`.
        :raises E2Error: If cancellation fails.
        """
        _log.info("E2 KPM unsubscribe  sub_id=%s", subscription_id)
        self._client.unsubscribe_kpm(subscription_id)

    def indication_to_kpi_report(self, indication: E2Indication) -> KpiReport:
        """Convert an :class:`E2Indication` to a :class:`~models.KpiReport`.

        Maps E2SM-KPM PM counter names (3GPP TS 28.552) directly to
        :class:`~models.KpiReport` fields.

        :param indication: Decoded E2 Indication from :meth:`E2Client.register_indication_handler`.
        :return: Standardised :class:`~models.KpiReport`.
        """
        c = indication.pm_counters
        return KpiReport(
            cell_id=indication.cell_id,
            gnb_id=indication.gnb_id,
            prb_util_dl=c.get(ThreeGPPKpi.DRB_PRB_UTIL_DL.value, 0.0),
            prb_util_ul=c.get(ThreeGPPKpi.DRB_PRB_UTIL_UL.value, 0.0),
            active_ue_count=int(c.get(ThreeGPPKpi.RRC_CONN_MEAN.value, 0)),
            dl_throughput_kbps=c.get(ThreeGPPKpi.DRB_UE_THP_DL.value, 0.0),
            ul_throughput_kbps=c.get(ThreeGPPKpi.DRB_UE_THP_UL.value, 0.0),
            rsrp_dbm=c.get(ThreeGPPKpi.RSRP.value),
            rsrq_db=c.get(ThreeGPPKpi.RSRQ.value),
            sinr_db=c.get(ThreeGPPKpi.SINR.value),
        )


# ---------------------------------------------------------------------------
# SM-RC adapter
# ---------------------------------------------------------------------------


class E2SmRcAdapter:
    """Adapts :class:`~models.PolicyDecision` to E2SM-RC control requests.

    Maps BMW Lab internal policy decisions to the E2SM-RC control action
    identifiers used by the target Near-RT RIC platform.

    :param e2_client: An :class:`E2Client` implementation.
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


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class E2Error(RuntimeError):
    """Raised when an E2 interface operation fails."""
