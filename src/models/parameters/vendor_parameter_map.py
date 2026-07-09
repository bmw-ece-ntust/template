"""Vendor-to-3GPP parameter translation table (Adapter pattern support)."""

from __future__ import annotations

from collections.abc import KeysView

from models.parameters.three_gpp_kpi import ThreeGPPKpi


class VendorParameterMap:
    """Maps proprietary vendor metric names to :class:`ThreeGPPKpi` identifiers.

    Declare one module-level map per vendor platform factory (e.g.
    :data:`factories.viavi.VIAVI_PARAM_MAP`)::

        VENDOR_PARAM_MAP = VendorParameterMap({
            "dl_prb_usage_pct": ThreeGPPKpi.DRB_PRB_UTIL_DL,
            "ul_prb_usage_pct": ThreeGPPKpi.DRB_PRB_UTIL_UL,
            "active_ue_count":  ThreeGPPKpi.RRC_CONN_MEAN,
        })

    This makes the Adapter pattern's translation table auditable and
    directly traceable to the 3GPP specification.

    :param mapping: ``{vendor_key: ThreeGPPKpi}`` translation table.
    """

    def __init__(self, mapping: dict[str, ThreeGPPKpi]) -> None:
        self._map = mapping

    def translate(self, vendor_key: str) -> ThreeGPPKpi | None:
        """Return the 3GPP KPI identifier for a vendor metric key.

        :param vendor_key: Proprietary metric key.
        :return: Matching :class:`ThreeGPPKpi`, or ``None`` if unmapped.
        """
        return self._map.get(vendor_key)

    def keys(self) -> KeysView[str]:
        """Return the proprietary vendor metric keys known to this map.

        :return: View of all mapped vendor keys.
        """
        return self._map.keys()

    def raw_to_standard(self, raw: dict[str, float]) -> dict[ThreeGPPKpi, float]:
        """Translate a raw vendor metric dict to 3GPP-keyed values.

        Unmapped keys are silently dropped.

        :param raw: ``{vendor_key: value}`` dict from the telemetry client.
        :return: ``{ThreeGPPKpi: value}`` for all recognized keys.
        """
        return {self._map[k]: v for k, v in raw.items() if k in self._map}
