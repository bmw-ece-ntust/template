"""Abstract Factory for VIAVI RIC Test simulation deployments."""

from __future__ import annotations

from factories.osc import OscPlatformFactory
from factories.viavi.kpi_analyzer import ViaviKpiAnalyzer


class ViaviPlatformFactory(OscPlatformFactory):
    """Abstract Factory for VIAVI RIC Test (RSG) simulation deployments.

    VIAVI exposes standard O-RAN interfaces (via the BMW Lab TA rApp or the
    RIC Test O-RAN layer), so this factory inherits the SME/ICS transport
    from :class:`~factories.osc.OscPlatformFactory` and overrides only the
    analyzer product: KPI payloads arrive with VIAVI naming and must pass
    through the :class:`~factories.viavi.ViaviKpiAnalyzer` Adapter.

    Simulator lifecycle (start/stop scenarios, UE configuration) remains the
    TA rApp's responsibility — this rApp never calls VIAVI RSG APIs directly.

    :param sme_base_url: Non-RT RIC SME API base URL.
    :param ics_base_url: Non-RT RIC ICS API base URL.
    :param service_name: rApp service name for SME registration.
    :param instance_id: Unique rApp instance ID for SME registration.
    :param callback_url: rApp-side URL for SME/ICS push callbacks.
    :param cell_id: Primary cell ID for telemetry collection and analysis.
    :param gnb_id: Parent gNB identifier for produced reports.
    :param ics_data_types: ICS data type IDs to subscribe to.

    :Example:

        >>> factory = ViaviPlatformFactory(
        ...     sme_base_url="http://nonrtric:8090",
        ...     ics_base_url="http://nonrtric:8083",
        ...     service_name="energy-saving-rapp",
        ...     instance_id="es-rapp-01",
        ...     callback_url="http://es-rapp:8080/r1/callback",
        ...     cell_id="S1/B2/C1",
        ... )
        >>> factory.create_kpi_analyzer().analyze({"PEE.AvgPower": 380.0}).avg_power_w
        380.0
    """

    def __init__(
        self,
        sme_base_url: str,
        ics_base_url: str,
        service_name: str,
        instance_id: str,
        callback_url: str,
        cell_id: str,
        gnb_id: str = "",
        ics_data_types: list[str] | None = None,
    ) -> None:
        super().__init__(
            sme_base_url=sme_base_url,
            ics_base_url=ics_base_url,
            service_name=service_name,
            instance_id=instance_id,
            callback_url=callback_url,
            cell_id=cell_id,
            ics_data_types=ics_data_types,
        )
        self._gnb_id = gnb_id

    def create_kpi_analyzer(self) -> ViaviKpiAnalyzer:
        """Create a :class:`~factories.viavi.ViaviKpiAnalyzer` for this factory's cell.

        :return: :class:`~factories.viavi.ViaviKpiAnalyzer`.
        """
        return ViaviKpiAnalyzer(self._cell_id, self._gnb_id)
