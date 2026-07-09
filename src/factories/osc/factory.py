"""Abstract Factory for O-RAN SC Non-RT RIC deployments."""

from __future__ import annotations

from factories import RAppPlatformFactory
from factories.osc.kpi_analyzer import OscKpiAnalyzer
from factories.osc.lifecycle_runner import OscLifecycleRunner
from factories.osc.telemetry_collector import OscIcsTelemetryCollector
from handlers.interfaces.r1 import ICSAdapter, SMEAdapter


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
        """Create an :class:`~factories.osc.OscLifecycleRunner` for SME/ICS lifecycle management.

        :return: Configured :class:`~factories.osc.OscLifecycleRunner`.
        """
        return OscLifecycleRunner(self._sme, self._ics, self._ics_data_types)

    def create_telemetry_collector(self) -> OscIcsTelemetryCollector:
        """Create an :class:`~factories.osc.OscIcsTelemetryCollector` bound to the first ICS job.

        :return: Collector polling the first subscribed ICS job.
        """
        job_id = f"{self._ics_data_types[0].lower().replace('_', '-')}-job"
        return OscIcsTelemetryCollector(ics_base_url=self._ics_base_url, job_id=job_id)

    def create_kpi_analyzer(self) -> OscKpiAnalyzer:
        """Create an :class:`~factories.osc.OscKpiAnalyzer` bound to this factory's cell.

        :return: Analyzer for the configured cell ID.
        """
        return OscKpiAnalyzer(self._cell_id)
