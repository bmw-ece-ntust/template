"""Parsed VES event envelope."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from handlers.interfaces.ves.common_header import VesCommonHeader


@dataclass(frozen=True)
class VesEvent:
    """Parsed VES event envelope.

    :param header: :class:`~handlers.interfaces.ves.VesCommonHeader`.
    :param body: Domain-specific event payload (fault, measurement, etc.).
    """

    header: VesCommonHeader
    body: dict[str, Any] = field(default_factory=dict)
