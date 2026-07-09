"""Abstract Factory for OpenAirInterface (FlexRIC) deployments."""

from __future__ import annotations

from factories.oai.kpi_analyzer import OaiKpiAnalyzer
from factories.osc import OscPlatformFactory


class OaiPlatformFactory(OscPlatformFactory):
    """Abstract Factory for OpenAirInterface gNB deployments via FlexRIC.

    OAI gNBs attach to the RIC through the standard E2 interface (FlexRIC),
    so this factory inherits the SME/ICS transport from
    :class:`~factories.osc.OscPlatformFactory` and overrides only the
    analyzer product: KPM payloads arrive with OAI naming and must pass
    through the :class:`~factories.oai.OaiKpiAnalyzer` Adapter.

    :param sme_base_url: Non-RT RIC SME API base URL.
    :param ics_base_url: Non-RT RIC ICS API base URL.
    :param service_name: rApp service name for SME registration.
    :param instance_id: Unique rApp instance ID for SME registration.
    :param callback_url: rApp-side URL for SME/ICS push callbacks.
    :param cell_id: Primary cell ID for telemetry collection and analysis.
    :param gnb_id: Parent gNB identifier for produced reports.
    :param ics_data_types: ICS data type IDs to subscribe to.
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

    def create_kpi_analyzer(self) -> OaiKpiAnalyzer:
        """Create an :class:`~factories.oai.OaiKpiAnalyzer` for this factory's cell.

        :return: :class:`~factories.oai.OaiKpiAnalyzer`.
        """
        return OaiKpiAnalyzer(self._cell_id, self._gnb_id)
