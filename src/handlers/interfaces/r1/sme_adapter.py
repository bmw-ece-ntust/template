"""R1 SME adapter — rApp service registration and discovery."""

from __future__ import annotations

import logging
from typing import Any

import requests

from handlers.interfaces.r1.sme_error import R1SMEError

_log = logging.getLogger(__name__)


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
