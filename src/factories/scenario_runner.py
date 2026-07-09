"""Abstract scenario runner — rApp lifecycle control product."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ScenarioRunner(ABC):
    """Controls the rApp lifecycle (register with SME, subscribe ICS, start)."""

    @abstractmethod
    def start(self) -> None:
        """Start the scenario / register lifecycle."""

    @abstractmethod
    def stop(self) -> None:
        """Stop the scenario / deregister lifecycle."""
