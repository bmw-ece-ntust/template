"""3GPP-aligned KPI data models for rApp core logic.

All parameter names are linked to their authoritative specifications
as required by the BMW Lab SOP source-code-guide §8.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PolicyDecision(Enum):
    """RAN policy decision output from the optimization strategy."""

    ACTIVE = "active"
    SLEEP = "sleep"
    HANDOVER = "handover"


@dataclass(frozen=True)
class KpiReport:
    """Standardized 3GPP KPI report consumed by optimization strategies.

    :param cell_id: NR Cell Global ID.
    :param prb_util_dl: DL PRB utilization ratio
        (`DRB.PrbUtilDL <https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/>`_,
        TS 28.552 §5.1.1.12.1).
    :param prb_util_ul: UL PRB utilization ratio
        (`DRB.PrbUtilUL <https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/>`_,
        TS 28.552 §5.1.1.12.2).
    :param active_ue_count: Number of active UEs in the cell.
    """

    cell_id: str
    prb_util_dl: float
    prb_util_ul: float
    active_ue_count: int
