"""ICS job-result polling telemetry collector for OSC deployments."""

from __future__ import annotations

import logging

import requests

from factories import TelemetryCollector

_log = logging.getLogger(__name__)


class OscIcsTelemetryCollector(TelemetryCollector):
    """Collects telemetry by polling ICS job results from the Non-RT RIC.

    In production the Non-RT RIC pushes data to the rApp's callback URL.
    This collector provides a synchronous polling alternative that is
    suitable for integration tests and lab deployments where a push receiver
    is not available.

    :param ics_base_url: ICS API base URL.
    :param job_id: ICS job ID to poll for results.

    .. note::

        For production deployments, replace polling with a push-receiver
        endpoint (e.g. a FastAPI route that writes incoming batches to a
        shared queue consumed by this class).
    """

    _RESULT_PATH = "/data-consumer/v1/info-jobs/{job_id}/result"

    def __init__(self, ics_base_url: str, job_id: str) -> None:
        self._base = ics_base_url.rstrip("/")
        self._job_id = job_id
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    def collect(self) -> dict[str, float]:
        """Poll ICS for the latest job result and return raw PM counters.

        :return: Flat dict of 3GPP PM counter name → raw float value
            (e.g. ``{"DRB.PrbUtilDL": 0.45, "RRC.ConnMean": 12.0}``).
        :raises RuntimeError: If the ICS HTTP request fails.
        """
        url = self._base + self._RESULT_PATH.format(job_id=self._job_id)
        _log.debug("ICS poll  %s", url)
        try:
            resp = self._session.get(url, timeout=10)
            resp.raise_for_status()
            return {k: float(v) for k, v in resp.json().items() if isinstance(v, (int, float))}
        except requests.RequestException as exc:
            raise RuntimeError(f"ICS poll failed for job {self._job_id!r}: {exc}") from exc
