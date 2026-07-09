"""Abstract E2 client — transport-independent interface (RMR or gRPC)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from handlers.interfaces.e2.control_ack import E2ControlAck
from handlers.interfaces.e2.control_request import E2ControlRequest
from handlers.interfaces.e2.indication import E2Indication


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
