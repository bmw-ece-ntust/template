"""RIC Control Request payload for E2SM-RC."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class E2ControlRequest:
    """RIC Control Request payload for E2SM-RC.

    :param ran_function_id: RAN function ID for E2SM-RC.
    :param cell_id: Target cell NR CGI.
    :param action_id: E2SM-RC control action identifier.
    :param action_params: Key-value pairs of control parameters.
    """

    ran_function_id: int
    cell_id: str
    action_id: int
    action_params: dict[str, Any] = field(default_factory=dict)
