"""A1 policy adapter — map BMW Lab PolicyDecision to O-RAN A1 policy JSON.

The A1 interface (O-RAN WG2 A1-AP) carries policy objects from the Non-RT RIC
to Near-RT RICs.  An rApp influences RAN behaviour by creating or updating A1
policy instances through the Non-RT RIC's A1 Policy Management Service.

Adapter role
    Translates BMW Lab's internal :class:`models.PolicyDecision` (the
    output of an :class:`controllers.strategies.OptimizationStrategy`) to
    O-RAN-standardised A1 policy JSON, and vice-versa for policy-status
    responses.

    .. code-block:: none

        [models.PolicyDecision] <── A1Adapter ──> [O-RAN A1 policy JSON]

A1 policy type used in this template
    ``ORAN_TrafficSteering_0.1.0`` — the standard OSC reference policy type
    that steers traffic by setting per-cell admission and preference
    parameters on the Near-RT RIC.  Override :attr:`A1Adapter.policy_type_id`
    to use a different policy type schema.

OSC reference
    ``nonrtric/plt/a1policymanagementservice``
    https://gerrit.o-ran-sc.org/r/gitweb?p=nonrtric/plt/a1policymanagementservice.git

One class per module (SOP programming.md Section 5.1); this package
re-exports the public API so callers keep writing
``from handlers.interfaces.a1 import A1Adapter``.

Pattern reference
    Adapter: https://refactoring.guru/design-patterns/adapter
"""

from __future__ import annotations

from handlers.interfaces.a1.adapter import A1Adapter
from handlers.interfaces.a1.error import A1Error

__all__ = [
    "A1Adapter",
    "A1Error",
]
