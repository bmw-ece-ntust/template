"""R1 interface adapters — Service Management Exposure (SME) and
Information Coordination Service (ICS / DME).

The R1 interface (O-RAN WG2 R1-AP) connects rApps to the Non-RT RIC
Service Management and Orchestration framework.  It has two key sub-services:

SME (Service Management Exposure)
    rApp lifecycle management: register services on startup, deregister on
    shutdown, and discover other rApps or enrichment-info producers.

ICS / DME (Information Coordination Service / Data Management Exposure)
    Data-as-a-service for rApps: subscribe to a typed data producer (e.g.
    cell-level KPM reports) and receive asynchronous push callbacks.

Adapter role
    Translates the Non-RT RIC REST APIs (O-RAN standard) to/from BMW Lab
    internal types.  :class:`SMEAdapter` manages the rApp service lifecycle;
    :class:`ICSAdapter` manages data subscriptions.

    .. code-block:: none

        [O-RAN R1 SME REST JSON] <── SMEAdapter ──> [rApp lifecycle state]
        [O-RAN R1 ICS REST JSON] <── ICSAdapter ──> [models.KpiReport]

OSC reference
    ``nonrtric/plt/rappmanager`` — ``threshold-control-rapp`` ``SMEClient``
    https://gerrit.o-ran-sc.org/r/gitweb?p=nonrtric/plt/rappmanager.git

Used by the OSC factory to register the rApp (SME) and subscribe to telemetry
(ICS) on startup.
"""

from __future__ import annotations

import logging
from typing import Any

import requests

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# SME — Service Management Exposure
# ---------------------------------------------------------------------------


class SMEAdapter:
    """Registers and deregisters the rApp with the Non-RT RIC SME.

    On :meth:`register` the rApp publishes its service metadata so that other
    rApps and the Non-RT RIC can discover it.  On :meth:`deregister` the
    registration is removed to allow clean lifecycle management.

    :param sme_base_url: Base URL of the Non-RT RIC SME API
        (e.g. ``http://nonrtric.svc.cluster.local:8090``).
    :param service_name: Human-readable rApp service name
        (e.g. ``"energy-saving-rapp"``).
    :param instance_id: Unique instance identifier
        (e.g. ``"energy-saving-rapp-01"``).
    :param callback_url: URL that the Non-RT RIC will use to push policy
        updates or enrichment info to this rApp instance.

    :Example:

        >>> sme = SMEAdapter(
        ...     sme_base_url="http://nonrtric:8090",
        ...     service_name="energy-saving-rapp",
        ...     instance_id="es-rapp-01",
        ...     callback_url="http://es-rapp-01.nonrtric.svc:8080/r1/callback",
        ... )
        >>> sme.register()
        >>> sme.keep_alive()
        >>> sme.deregister()

    .. note::

        The registration payload follows the O-RAN SC Non-RT RIC A1 Policy
        Management Service API (``/a1-policy/v2/services``).
        Refer to ``nonrtric/plt/a1policymanagementservice`` for the full schema.
    """

    _REGISTER_PATH = "/a1-policy/v2/services"

    def __init__(
        self,
        sme_base_url: str,
        service_name: str,
        instance_id: str,
        callback_url: str,
    ) -> None:
        self._base = sme_base_url.rstrip("/")
        self._service_name = service_name
        self._instance_id = instance_id
        self._callback_url = callback_url
        self._session = requests.Session()
        self._session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )
        self._registered = False

    # --- R1SMEPort implementation -------------------------------------------

    def register(self) -> None:
        """Publish this rApp's service registration to SME.

        :raises R1SMEError: If the Non-RT RIC SME rejects the registration.
        """
        url = f"{self._base}{self._REGISTER_PATH}/{self._instance_id}"
        body: dict[str, Any] = {
            "callbackUrl": self._callback_url,
            "keepAliveIntervalSeconds": 20,
            "serviceName": self._service_name,
        }
        _log.info(
            "SME register  service=%s  instance=%s",
            self._service_name,
            self._instance_id,
        )
        try:
            resp = self._session.put(url, json=body, timeout=10)
            resp.raise_for_status()
            self._registered = True
            _log.info("SME registration successful")
        except requests.RequestException as exc:
            raise R1SMEError(f"SME register failed: {exc}") from exc

    def deregister(self) -> None:
        """Remove this rApp's service registration from SME.

        No-op if not currently registered.

        :raises R1SMEError: If the Non-RT RIC SME rejects deregistration.
        """
        if not self._registered:
            return
        url = f"{self._base}{self._REGISTER_PATH}/{self._instance_id}"
        _log.info("SME deregister  instance=%s", self._instance_id)
        try:
            resp = self._session.delete(url, timeout=10)
            resp.raise_for_status()
            self._registered = False
            _log.info("SME deregistration successful")
        except requests.RequestException as exc:
            raise R1SMEError(f"SME deregister failed: {exc}") from exc

    def keep_alive(self) -> None:
        """Send a keep-alive heartbeat to prevent automatic deregistration.

        Call this periodically at an interval shorter than
        ``keepAliveIntervalSeconds`` (registered as 20 s by default).

        :raises R1SMEError: If the heartbeat is rejected.
        """
        url = f"{self._base}{self._REGISTER_PATH}/{self._instance_id}"
        _log.debug("SME keep_alive  instance=%s", self._instance_id)
        try:
            resp = self._session.put(url, json={}, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise R1SMEError(f"SME keep_alive failed: {exc}") from exc

    def discover_services(self, service_name: str | None = None) -> list[dict[str, Any]]:
        """Discover registered rApp services from the Non-RT RIC SME.

        :param service_name: If provided, filter results to this service name.
        :return: List of service registration objects.
        :raises R1SMEError: On HTTP error.
        """
        url = f"{self._base}{self._REGISTER_PATH}"
        params: dict[str, str] = {}
        if service_name:
            params["service_id"] = service_name
        try:
            resp = self._session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            services: list[dict[str, Any]] = resp.json()
            return services
        except requests.RequestException as exc:
            raise R1SMEError(f"SME discover_services failed: {exc}") from exc


# ---------------------------------------------------------------------------
# ICS — Information Coordination Service / Data Management Exposure
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class R1SMEError(RuntimeError):
    """Raised when an R1 SME operation fails."""


class R1ICSError(RuntimeError):
    """Raised when an R1 ICS operation fails."""
