"""Application-layer port contracts (structural typing via :mod:`typing.Protocol`).

A *port* is the boundary between the application core and the outside world.
Each Protocol defines *what* the application layer needs without constraining
*how* it is implemented.  Any class whose methods match satisfies it — no
explicit inheritance required.

Port taxonomy
    **Inbound** (outside → application):
        :class:`HealthPort`, :class:`IntentPort`, :class:`VESPort`

    **Outbound** (application → outside):
        :class:`O1Port`, :class:`R1SMEPort`, :class:`R1ICSPort`, :class:`A1Port`,
        :class:`E2KpmPort`, :class:`E2RcPort`, :class:`TopologyPort`

Adapter implementations
    * :class:`rapp.adapters.o1.O1SdncAdapter`        → :class:`O1Port`
    * :class:`rapp.adapters.r1.SMEAdapter`            → :class:`R1SMEPort`
    * :class:`rapp.adapters.r1.ICSAdapter`            → :class:`R1ICSPort`
    * :class:`rapp.adapters.a1.A1Adapter`             → :class:`A1Port`
    * :class:`rapp.adapters.e2.E2SmKpmAdapter`        → :class:`E2KpmPort`
    * :class:`rapp.adapters.e2.E2SmRcAdapter`         → :class:`E2RcPort`
    * :class:`rapp.adapters.ves.VesEventAdapter`      → :class:`VESPort`
    * :class:`rapp.adapters.teiv.TEIVAdapter`         → :class:`TopologyPort`
    * :class:`rapp.domain.intent.IntentResolutionService` → :class:`IntentPort`
"""

from __future__ import annotations

from typing import Any, Callable, Protocol

from rapp.domain.models import Health


# ---------------------------------------------------------------------------
# Inbound ports
# ---------------------------------------------------------------------------

class HealthPort(Protocol):
    """Port for health-check operations."""

    def get_health(self) -> Health:
        """Return the current health status of the service.

        :return: :class:`~rapp.domain.models.Health`
        """
        ...


class IntentPort(Protocol):
    """Port for receiving contract-based IBN intents (inbound).

    Implemented by :class:`~rapp.domain.intent.IntentResolutionService`.
    Called by the ICS callback handler when an intent contract arrives.

    Ref: IETF RFC 9315 — Intent-based Networking Concepts.
    """

    def validate(self, contract: Any) -> bool:
        """Validate an incoming intent contract (whitelist + expiry + signature).

        :param contract: :class:`~rapp.domain.intent.IntentContract`.
        :return: ``True`` if valid.
        :raises rapp.domain.intent.IntentValidationError: If invalid.
        """
        ...

    def resolve(self, contract: Any, kpis: Any) -> str:
        """Resolve a validated contract to a policy decision string.

        :param contract: Validated :class:`~rapp.domain.intent.IntentContract`.
        :param kpis: Current :class:`~core.models.KpiReport`.
        :return: :class:`~core.models.PolicyDecision` value string.
        """
        ...


class VESPort(Protocol):
    """Port for receiving inbound VES event push (inbound).

    Implemented by :class:`~rapp.adapters.ves.VesEventAdapter`.
    Called by the ICS callback HTTP endpoint when a VES batch arrives.
    """

    def dispatch(self, raw: dict[str, Any]) -> Any:
        """Parse and dispatch a raw VES event payload.

        :param raw: Top-level VES JSON dict.
        :return: Parsed :class:`~rapp.adapters.ves.VesEvent` or ``None``.
        """
        ...


# ---------------------------------------------------------------------------
# Outbound ports — O-RAN standard interfaces
# ---------------------------------------------------------------------------

class O1Port(Protocol):
    """Port for O1 YANG cell-configuration operations.

    Satisfied by :class:`rapp.adapters.o1.O1SdncAdapter`.
    O1 reference: O-RAN.WG5.O1, 3GPP TS 28.535.
    """

    def get_cell_config(self, cell_id: str) -> dict[str, Any]:
        """Retrieve the current YANG configuration for a cell.

        :param cell_id: NR Cell Global ID.
        :return: Flat YANG attribute-name → value mapping.
        :raises rapp.adapters.o1.O1Error: If unreachable.
        """
        ...

    def set_cell_config(self, cell_id: str, config: dict[str, Any]) -> None:
        """Apply a partial YANG configuration patch to a cell.

        :param cell_id: NR Cell Global ID.
        :param config: Partial YANG attribute-name → new value mapping.
        :raises rapp.adapters.o1.O1Error: If rejected.
        """
        ...


class R1SMEPort(Protocol):
    """Port for R1 Service Management Exposure (SME) lifecycle operations.

    Satisfied by :class:`rapp.adapters.r1.SMEAdapter`.
    R1/SME reference: O-RAN WG2 R1-AP.
    """

    def register(self) -> None:
        """Register this rApp with the Non-RT RIC SME.

        :raises rapp.adapters.r1.R1SMEError: If rejected.
        """
        ...

    def deregister(self) -> None:
        """Deregister this rApp from the Non-RT RIC SME.

        :raises rapp.adapters.r1.R1SMEError: If it fails.
        """
        ...


class R1ICSPort(Protocol):
    """Port for R1 Information Coordination Service (ICS / DME) operations.

    Satisfied by :class:`rapp.adapters.r1.ICSAdapter`.
    R1/ICS reference: O-RAN WG2 R1-AP (Data Management and Exposure).
    """

    def subscribe(self, data_type_id: str, job_id: str | None = None) -> str:
        """Subscribe to an ICS data type.

        :param data_type_id: ICS data type identifier.
        :param job_id: Optional explicit job ID.
        :return: The ICS job ID.
        :raises rapp.adapters.r1.R1ICSError: If rejected.
        """
        ...

    def unsubscribe(self, job_id: str) -> None:
        """Cancel an ICS data subscription.

        :param job_id: ICS job ID returned by :meth:`subscribe`.
        :raises rapp.adapters.r1.R1ICSError: If cancellation fails.
        """
        ...


class A1Port(Protocol):
    """Port for A1 policy management operations.

    Satisfied by :class:`rapp.adapters.a1.A1Adapter`.
    A1 reference: O-RAN WG2 A1-AP.
    """

    def create_policy(
        self,
        near_rt_ric_id: str,
        cell_id: str,
        decision: Any,
        policy_id: str | None = None,
    ) -> str:
        """Create or update an A1 policy instance.

        :param near_rt_ric_id: Target Near-RT RIC identifier.
        :param cell_id: NR Cell Global ID.
        :param decision: :class:`~core.models.PolicyDecision`.
        :param policy_id: Auto-generated if ``None``.
        :return: Policy ID.
        :raises rapp.adapters.a1.A1Error: If rejected.
        """
        ...

    def delete_policy(self, policy_id: str) -> None:
        """Delete an A1 policy instance.

        :param policy_id: Policy ID from :meth:`create_policy`.
        :raises rapp.adapters.a1.A1Error: If deletion fails.
        """
        ...


class E2KpmPort(Protocol):
    """Port for E2SM-KPM subscription operations (outbound to Near-RT RIC).

    Satisfied by :class:`rapp.adapters.e2.E2SmKpmAdapter`.
    E2SM-KPM reference: O-RAN.WG3.E2SM-KPM-v03.00.
    """

    def subscribe(self, cell_id: str, interval_ms: int = 1000) -> str:
        """Subscribe to KPM reports for a cell.

        :param cell_id: Target cell NR CGI.
        :param interval_ms: Granularity period in milliseconds.
        :return: Subscription ID.
        :raises rapp.adapters.e2.E2Error: If rejected.
        """
        ...

    def unsubscribe(self, subscription_id: str) -> None:
        """Cancel a KPM subscription.

        :param subscription_id: ID from :meth:`subscribe`.
        :raises rapp.adapters.e2.E2Error: If cancellation fails.
        """
        ...

    def indication_to_kpi_report(self, indication: Any) -> Any:
        """Convert an E2 Indication to a :class:`~core.models.KpiReport`.

        :param indication: :class:`~rapp.adapters.e2.E2Indication`.
        :return: :class:`~core.models.KpiReport`.
        """
        ...


class E2RcPort(Protocol):
    """Port for E2SM-RC control operations (outbound to Near-RT RIC).

    Satisfied by :class:`rapp.adapters.e2.E2SmRcAdapter`.
    E2SM-RC reference: O-RAN.WG3.E2SM-RC-v01.03.
    """

    def apply_decision(
        self,
        cell_id: str,
        decision: Any,
        extra_params: dict[str, Any] | None = None,
    ) -> Any:
        """Send an E2SM-RC control request for a policy decision.

        :param cell_id: Target cell NR CGI.
        :param decision: :class:`~core.models.PolicyDecision`.
        :param extra_params: Additional E2SM-RC control parameters.
        :return: :class:`~rapp.adapters.e2.E2ControlAck`.
        :raises rapp.adapters.e2.E2Error: If rejected.
        """
        ...


class TopologyPort(Protocol):
    """Port for network topology discovery (outbound to TEIV).

    Satisfied by :class:`rapp.adapters.teiv.TEIVAdapter`.
    """

    def load_topology(self) -> Any:
        """Fetch all cells from TEIV and return a :class:`~rapp.domain.topology.NetworkTopology`.

        :return: Populated :class:`~rapp.domain.topology.NetworkTopology`.
        :raises rapp.adapters.teiv.TEIVError: If unreachable.
        """
        ...
