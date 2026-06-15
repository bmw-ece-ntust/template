"""Proprietary vendor adapters — multi-vendor O-RAN support (Adapter pattern).

This package isolates **vendor-proprietary** parameter handling from the
O-RAN **standard** interface adapters in
:mod:`handlers.interfaces`.  Each vendor gets its own subpackage
(``ericsson/``, ``nokia/`` …) declaring:

1. A proprietary parameter ``str`` enum (the vendor's own metric names).
2. A :class:`~models.parameters.VendorParameterMap` translating those
   names to spec-traceable :class:`~models.parameters.ThreeGPPKpi`
   identifiers.
3. A concrete :class:`VendorAdapter` that fetches raw telemetry and emits a
   standard :class:`~models.KpiReport`.

Core, domain, and application code never import a vendor subpackage directly;
they resolve an adapter through :func:`get_vendor_adapter`, keeping rApp logic
vendor-agnostic.  This realises BMW Lab SOP source-code-guide Section 3.1
(Adapter pattern) and Architectural Rule 6 (vendor mapping is adapter work).

Reference: https://refactoring.guru/design-patterns/adapter

:Example:

    >>> from handlers.adapters import get_vendor_adapter
    >>> adapter = get_vendor_adapter("ericsson", client=my_ericsson_client)
    >>> report = adapter.to_kpi_report("cell-001", gnb_id="gnb-1")
"""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from handlers.vendor import VendorTelemetryClient
from models import KpiReport
from models.parameters import NodeType, ThreeGPPKpi, VendorParameterMap


class VendorAdapter(ABC):
    """Base class for a vendor-proprietary telemetry adapter.

    Subclasses set three class variables and inherit the translation logic:

    :cvar VENDOR: Lowercase vendor identifier used for registry lookup.
    :cvar PARAM_MAP: Proprietary-key to :class:`ThreeGPPKpi`
        :class:`~models.parameters.VendorParameterMap`.
    :cvar NODE_TYPE: Default :class:`~models.parameters.NodeType`
        for nodes managed by this vendor adapter.

    :param client: Vendor telemetry source implementing
        :class:`~handlers.vendor.VendorTelemetryClient`.
    """

    VENDOR: ClassVar[str]
    PARAM_MAP: ClassVar[VendorParameterMap]
    NODE_TYPE: ClassVar[NodeType] = NodeType.GNB

    def __init__(self, client: VendorTelemetryClient) -> None:
        self._client = client

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Auto-register concrete vendor adapters by their ``VENDOR`` id."""
        super().__init_subclass__(**kwargs)
        vendor = getattr(cls, "VENDOR", None)
        if vendor:
            _REGISTRY[vendor.lower()] = cls

    def fetch_kpi_values(self) -> dict[ThreeGPPKpi, float]:
        """Fetch every mapped proprietary metric as a 3GPP-keyed dict.

        Missing or non-numeric vendor metrics are skipped, so a partial
        telemetry response still yields a usable report.

        :return: ``{ThreeGPPKpi: float}`` for all resolvable keys.
        """
        values: dict[ThreeGPPKpi, float] = {}
        for vendor_key in self.PARAM_MAP.keys():  # noqa: SIM118 — VendorParameterMap, not a dict
            kpi = self.PARAM_MAP.translate(vendor_key)
            if kpi is None:
                continue
            try:
                values[kpi] = float(self._client.get_metric(vendor_key))
            except (KeyError, ValueError, TypeError):
                continue
        return values

    def to_kpi_report(self, cell_id: str, gnb_id: str = "") -> KpiReport:
        """Produce a standard :class:`~models.KpiReport` for a cell.

        :param cell_id: NR Cell Global ID.
        :param gnb_id: Parent gNB identifier.
        :return: Vendor-agnostic :class:`~models.KpiReport`.
        """
        return KpiReport.from_3gpp(
            cell_id, self.fetch_kpi_values(), gnb_id=gnb_id, node_type=self.NODE_TYPE
        )


#: vendor id → concrete :class:`VendorAdapter` subclass (populated on import).
_REGISTRY: dict[str, type[VendorAdapter]] = {}


def get_vendor_adapter(vendor: str, client: VendorTelemetryClient) -> VendorAdapter:
    """Resolve and instantiate a vendor adapter by name.

    :param vendor: Vendor identifier (case-insensitive), e.g. ``"ericsson"``.
    :param client: Vendor telemetry client to wrap.
    :return: Instantiated :class:`VendorAdapter`.
    :raises KeyError: If no adapter is registered for ``vendor``.
    """
    # Import subpackages lazily so their __init_subclass__ runs and registers.
    from handlers.adapters import ericsson, nokia  # noqa: F401

    key = vendor.lower()
    if key not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY)) or "none"
        raise KeyError(f"No vendor adapter for {vendor!r}. Available: {available}.")
    return _REGISTRY[key](client)


def registered_vendors() -> list[str]:
    """Return the sorted list of registered vendor identifiers.

    :return: Vendor ids with an available adapter.
    """
    from handlers.adapters import ericsson, nokia  # noqa: F401

    return sorted(_REGISTRY)
