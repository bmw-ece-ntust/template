from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Health:
    status: str
    service: str
    timestamp: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
