"""E2SM-KPM adapter — E2 indications to :class:`~models.KpiReport`."""

from __future__ import annotations

import logging

from handlers.interfaces.e2.client import E2Client
from handlers.interfaces.e2.indication import E2Indication
from models import KpiReport
from models.parameters import ThreeGPPKpi

_log = logging.getLogger(__name__)


class E2SmKpmAdapter:
    """Adapts E2SM-KPM indications to :class:`~models.KpiReport`.

    Decodes the raw PM counter payload from the E2 node and normalises it
    to the BMW Lab :class:`~models.KpiReport` data model.

    :param e2_client: An :class:`~handlers.interfaces.e2.E2Client` implementation.
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

        :param indication: Decoded E2 Indication from
            :meth:`~handlers.interfaces.e2.E2Client.register_indication_handler`.
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
