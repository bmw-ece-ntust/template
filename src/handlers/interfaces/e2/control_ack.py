"""Acknowledgement from the E2 node for a RIC Control Request."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class E2ControlAck:
    """Acknowledgement from the E2 node for a RIC Control Request.

    :param success: ``True`` if the control was accepted.
    :param message: Human-readable status message from the E2 node.
    """

    success: bool
    message: str = ""
