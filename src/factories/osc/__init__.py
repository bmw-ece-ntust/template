"""OSC Non-RT RIC platform factory — creates components for real O-RAN deployments.

Implements :class:`factories.RAppPlatformFactory` for O-RAN SC Non-RT RIC
environments where telemetry arrives via ICS data subscriptions and
cell configuration is pushed via O1/SDNC.

Platform-component mapping

    .. list-table::
       :header-rows: 1

       * - Abstract component
         - OSC implementation
         - Backing interface
       * - :class:`~factories.ScenarioRunner`
         - :class:`OscLifecycleRunner`
         - R1/SME (register) + R1/ICS (subscribe)
       * - :class:`~factories.TelemetryCollector`
         - :class:`OscIcsTelemetryCollector`
         - R1/ICS job-result polling
       * - :class:`~factories.KpiAnalyzer`
         - :class:`OscKpiAnalyzer`
         - 3GPP PM counter → :class:`~core.models.KpiReport`

Usage
    Use this factory when ``RAPP_PLATFORM=osc`` is set in the environment.
    For simulation, use :class:`factories.ns3.Ns3PlatformFactory` or
    :class:`factories.viavi.ViaviPlatformFactory` instead.

OSC reference
    ``nonrtric/plt/rappmanager``
    https://gerrit.o-ran-sc.org/r/gitweb?p=nonrtric/plt/rappmanager.git
"""

from __future__ import annotations

import logging

import requests

from core.models import KpiReport
from core.models.parameters import ThreeGPPKpi
from factories import KpiAnalyzer, RAppPlatformFactory, ScenarioRunner, TelemetryCollector
from rapp.adapters.r1 import ICSAdapter, R1ICSError, SMEAdapter

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ScenarioRunner — rApp lifecycle (SME register + ICS subscribe)
# ---------------------------------------------------------------------------

class OscLifecycleRunner(ScenarioRunner):
    """Manages the rApp lifecycle within the O-RAN SC Non-RT RIC.

    On :meth:`start`, registers the rApp with SME and subscribes to all
    configured ICS data types.  On :meth:`stop`, cancels subscriptions and
    deregisters from SME in reverse order for a clean shutdown.

    :param sme: Configured :class:`~rapp.adapters.r1.SMEAdapter` instance.
    :param ics: Configured :class:`~rapp.adapters.r1.ICSAdapter` instance.
    :param ics_data_types: List of ICS data type IDs to subscribe to
        (e.g. ``["PM_REPORT_CELL_LEVEL"]``).

    :Example:

        >>> runner = OscLifecycleRunner(sme, ics, ["PM_REPORT_CELL_LEVEL"])
        >>> runner.start()   # rApp is now registered and receiving data
        >>> runner.stop()    # graceful shutdown: unsubscribe then deregister
    """

    def __init__(
        self,
        sme: SMEAdapter,
        ics: ICSAdapter,
        ics_data_types: list[str],
    ) -> None:
        self._sme = sme
        self._ics = ics
        self._ics_data_types = ics_data_types

    def start(self) -> None:
        """Register with SME and subscribe to all configured ICS data types.

        :raises rapp.adapters.r1.R1SMEError: If SME registration fails.
        :raises rapp.adapters.r1.R1ICSError: If any ICS subscription fails.
        """
        _log.info("OscLifecycleRunner: starting")
        self._sme.register()
        for data_type in self._ics_data_types:
            self._ics.subscribe(data_type)
        _log.info("OscLifecycleRunner: started — subscribed to %s", self._ics_data_types)

    def stop(self) -> None:
        """Cancel all ICS subscriptions and deregister from SME.

        ICS errors are logged but not re-raised so that SME deregistration
        always runs even when some subscriptions fail to cancel.
        """
        _log.info("OscLifecycleRunner: stopping")
        self._ics.unsubscribe_all()
        self._sme.deregister()
        _log.info("OscLifecycleRunner: stopped")


# ---------------------------------------------------------------------------
# TelemetryCollector — ICS job-result polling
# ---------------------------------------------------------------------------

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
            raise RuntimeError(
                f"ICS poll failed for job {self._job_id!r}: {exc}"
            ) from exc


# ---------------------------------------------------------------------------
# KpiAnalyzer — raw ICS payload → KpiReport
# ---------------------------------------------------------------------------

class OscKpiAnalyzer(KpiAnalyzer):
    """Translates raw ICS PM counter payloads into standardized KPI reports.

    ICS delivers performance-measurement data using 3GPP counter names
    (e.g. ``DRB.PrbUtilDL``, ``RRC.ConnMean``).  This analyzer maps those
    names directly to :class:`~core.models.KpiReport` fields without any
    vendor-specific translation — the O-RAN standard guarantees the names.

    :param cell_id: NR Cell Global ID annotated in the produced report.

    :Example:

        >>> analyzer = OscKpiAnalyzer("o-du-1111/cell-0")
        >>> report = analyzer.analyze({"DRB.PrbUtilDL": 0.72, "RRC.ConnMean": 14.0})
    """

    def __init__(self, cell_id: str) -> None:
        self._cell_id = cell_id

    def analyze(self, raw: dict[str, float]) -> KpiReport:
        """Convert ICS raw PM counters to a :class:`~core.models.KpiReport`.

        Expected keys in *raw* (3GPP TS 28.552):

        - ``DRB.PrbUtilDL`` — DL PRB utilization ratio (Section 5.1.1.12.1)
        - ``DRB.PrbUtilUL`` — UL PRB utilization ratio (Section 5.1.1.12.2)
        - ``RRC.ConnMean``  — Mean number of active UE connections

        Missing keys default to ``0`` / ``0.0``.

        :param raw: Raw PM counter dict from :class:`OscIcsTelemetryCollector`.
        :return: Standardized :class:`~core.models.KpiReport`.
        """
        return KpiReport(
            cell_id=self._cell_id,
            prb_util_dl=raw.get(ThreeGPPKpi.DRB_PRB_UTIL_DL.value, 0.0),
            prb_util_ul=raw.get(ThreeGPPKpi.DRB_PRB_UTIL_UL.value, 0.0),
            active_ue_count=int(raw.get(ThreeGPPKpi.RRC_CONN_MEAN.value, 0)),
            dl_throughput_kbps=raw.get(ThreeGPPKpi.DRB_UE_THP_DL.value, 0.0),
            ul_throughput_kbps=raw.get(ThreeGPPKpi.DRB_UE_THP_UL.value, 0.0),
        )


# ---------------------------------------------------------------------------
# Abstract Factory — OscPlatformFactory
# ---------------------------------------------------------------------------

class OscPlatformFactory(RAppPlatformFactory):
    """Abstract factory for O-RAN SC Non-RT RIC deployments.

    Creates components that use the live O-RAN interfaces: ICS for telemetry
    ingestion, SME for lifecycle management, and O1/SDNC for cell control.

    :param sme_base_url: Non-RT RIC SME API base URL.
    :param ics_base_url: Non-RT RIC ICS API base URL.
    :param service_name: rApp service name for SME registration.
    :param instance_id: Unique rApp instance ID for SME registration.
    :param callback_url: rApp-side URL for SME/ICS push callbacks.
    :param cell_id: Primary cell ID for telemetry collection and analysis.
    :param ics_data_types: ICS data type IDs to subscribe to.
                            Defaults to ``["PM_REPORT_CELL_LEVEL"]``.

    :Example:

        >>> factory = OscPlatformFactory(
        ...     sme_base_url="http://nonrtric:8090",
        ...     ics_base_url="http://nonrtric:8083",
        ...     service_name="energy-saving-rapp",
        ...     instance_id="es-rapp-01",
        ...     callback_url="http://es-rapp.nonrtric.svc:8080/r1/callback",
        ...     cell_id="o-du-1111/cell-0",
        ...     ics_data_types=["PM_REPORT_CELL_LEVEL"],
        ... )
        >>> runner   = factory.create_scenario_runner()
        >>> collector = factory.create_telemetry_collector()
        >>> analyzer  = factory.create_kpi_analyzer()
        >>> runner.start()
    """

    def __init__(
        self,
        sme_base_url: str,
        ics_base_url: str,
        service_name: str,
        instance_id: str,
        callback_url: str,
        cell_id: str,
        ics_data_types: list[str] | None = None,
    ) -> None:
        self._ics_base_url = ics_base_url.rstrip("/")
        self._cell_id = cell_id
        self._ics_data_types = ics_data_types or ["PM_REPORT_CELL_LEVEL"]

        self._sme = SMEAdapter(sme_base_url, service_name, instance_id, callback_url)
        self._ics = ICSAdapter(ics_base_url, callback_url)

    def create_scenario_runner(self) -> OscLifecycleRunner:
        """Create an :class:`OscLifecycleRunner` for SME/ICS lifecycle management.

        :return: Configured :class:`OscLifecycleRunner`.
        """
        return OscLifecycleRunner(self._sme, self._ics, self._ics_data_types)

    def create_telemetry_collector(self) -> OscIcsTelemetryCollector:
        """Create an :class:`OscIcsTelemetryCollector` bound to the first ICS job.

        :return: Collector polling the first subscribed ICS job.
        """
        job_id = f"{self._ics_data_types[0].lower().replace('_', '-')}-job"
        return OscIcsTelemetryCollector(ics_base_url=self._ics_base_url, job_id=job_id)

    def create_kpi_analyzer(self) -> OscKpiAnalyzer:
        """Create an :class:`OscKpiAnalyzer` bound to this factory's cell.

        :return: Analyzer for :attr:`cell_id`.
        """
        return OscKpiAnalyzer(self._cell_id)
