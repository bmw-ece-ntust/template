"""R1 ICS adapter — data subscriptions on the Non-RT RIC ICS / DME."""

from __future__ import annotations

import logging
from typing import Any

import requests

from handlers.interfaces.r1.ics_error import R1ICSError

_log = logging.getLogger(__name__)


class ICSAdapter:
    """Subscribes to and unsubscribes from ICS data producers in the Non-RT RIC.

    The ICS (also called DME — Data Management Exposure) lets rApps receive
    typed data streams (e.g. cell-level PM reports, UE traces) asynchronously
    via push callbacks, or poll results via the job-result endpoint.

    :param ics_base_url: Base URL of the ICS API
        (e.g. ``http://nonrtric.svc.cluster.local:8083``).
    :param callback_url: URL of the rApp's data ingestion endpoint.
                         ICS will POST data batches to this address.

    :Example:

        >>> ics = ICSAdapter(
        ...     ics_base_url="http://nonrtric:8083",
        ...     callback_url="http://my-rapp.nonrtric.svc:8080/r1/data",
        ... )
        >>> sub_id = ics.subscribe("PM_REPORT_CELL_LEVEL")
        >>> # ICS now POSTs PM reports to callback_url
        >>> ics.unsubscribe(sub_id)

    .. note::

        Data type IDs follow the O-RAN SC ICS / DME naming convention.
        Run ``GET /data-producer/v1/info-types`` against the ICS API to
        list available data types in your deployment.
    """

    _SUBSCRIPTION_PATH = "/data-consumer/v1/info-jobs"

    def __init__(self, ics_base_url: str, callback_url: str) -> None:
        self._base = ics_base_url.rstrip("/")
        self._callback_url = callback_url
        self._session = requests.Session()
        self._session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )
        self._active_subscriptions: dict[str, str] = {}  # data_type_id → job_id

    # --- R1ICSPort implementation -------------------------------------------

    def subscribe(self, data_type_id: str, job_id: str | None = None) -> str:
        """Subscribe to a data type produced by the Non-RT RIC ICS.

        :param data_type_id: ICS data type identifier
            (e.g. ``"PM_REPORT_CELL_LEVEL"``).
        :param job_id: Optional explicit job ID; auto-generated if ``None``.
        :return: The ICS job ID for this subscription.
        :raises R1ICSError: If the subscription is rejected by the ICS.
        """
        if job_id is None:
            job_id = f"{data_type_id.lower().replace('_', '-')}-job"
        url = f"{self._base}{self._SUBSCRIPTION_PATH}/{job_id}"
        body: dict[str, Any] = {
            "info_type_id": data_type_id,
            "job_result_uri": self._callback_url,
            "status_notification_uri": f"{self._callback_url}/status",
            "job_owner": "rapp-template",
            "job_definition": {},
        }
        _log.info("ICS subscribe  data_type=%s  job_id=%s", data_type_id, job_id)
        try:
            resp = self._session.put(url, json=body, timeout=10)
            resp.raise_for_status()
            self._active_subscriptions[data_type_id] = job_id
            _log.info("ICS subscription active  job_id=%s", job_id)
            return job_id
        except requests.RequestException as exc:
            raise R1ICSError(f"ICS subscribe({data_type_id!r}) failed: {exc}") from exc

    def unsubscribe(self, job_id: str) -> None:
        """Cancel an active ICS data subscription.

        :param job_id: ICS job ID returned by :meth:`subscribe`.
        :raises R1ICSError: If cancellation fails.
        """
        url = f"{self._base}{self._SUBSCRIPTION_PATH}/{job_id}"
        _log.info("ICS unsubscribe  job_id=%s", job_id)
        try:
            resp = self._session.delete(url, timeout=10)
            resp.raise_for_status()
            self._active_subscriptions = {
                k: v for k, v in self._active_subscriptions.items() if v != job_id
            }
        except requests.RequestException as exc:
            raise R1ICSError(f"ICS unsubscribe({job_id!r}) failed: {exc}") from exc

    def unsubscribe_all(self) -> None:
        """Cancel all active ICS subscriptions held by this adapter.

        Intended for graceful shutdown.  Individual errors are logged but
        not re-raised so that all subscriptions are attempted.
        """
        for data_type_id, job_id in list(self._active_subscriptions.items()):
            try:
                self.unsubscribe(job_id)
            except R1ICSError:
                _log.warning(
                    "ICS unsubscribe failed for job_id=%s (data_type=%s) during teardown",
                    job_id,
                    data_type_id,
                )
