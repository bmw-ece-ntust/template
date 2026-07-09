"""Abstract telemetry collector — raw PM data product."""

from __future__ import annotations

from abc import ABC, abstractmethod


class TelemetryCollector(ABC):
    """Collects raw PM counter data from the platform."""

    @abstractmethod
    def collect(self) -> dict[str, float]:
        """Collect raw telemetry.

        :return: ``{ThreeGPPKpi.value: float}`` mapping.
        """
