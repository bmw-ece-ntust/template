"""VES domain / event-type identifier enum."""

from __future__ import annotations

from enum import Enum


class VesEventType(str, Enum):
    """VES domain / event-type identifiers used in O-RAN SC deployments.

    Source: ONAP VES Listener 7.2 §5.4 (domain enumeration).
    """

    FAULT = "fault"
    MEASUREMENT = "measurement"
    NOTIFICATION = "notification"
    STATE_CHANGE = "stateChange"
    THRESHOLD_CROSSING = "thresholdCrossingAlert"
