from __future__ import annotations

from typing import Protocol

from rapp.domain.models import Health


class HealthPort(Protocol):
    def get_health(self) -> Health: ...
