"""Abstract KPI analyzer — raw PM data to :class:`~models.KpiReport` product."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import KpiReport


class KpiAnalyzer(ABC):
    """Converts raw PM data into a standardized :class:`~models.KpiReport`."""

    @abstractmethod
    def analyze(self, raw: dict[str, float]) -> KpiReport:
        """Map raw platform metrics to a standardized KPI report.

        :param raw: Raw metrics from
            :class:`~factories.TelemetryCollector`.
        :return: :class:`~models.KpiReport`.
        """
