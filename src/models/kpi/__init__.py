"""3GPP-aligned KPI data models for rApp/xApp core logic.

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from models.kpi import KpiReport, PolicyDecision``.
"""

from __future__ import annotations

from models.kpi.kpi_report import KpiReport
from models.kpi.policy_decision import PolicyDecision

__all__ = [
    "KpiReport",
    "PolicyDecision",
]
