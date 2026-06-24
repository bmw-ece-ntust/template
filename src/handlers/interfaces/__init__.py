"""O-RAN standard interface adapters (Adapter pattern).

Each module wraps one published O-RAN / 3GPP interface and maps it to the
template's internal value objects.  No proprietary vendor logic appears here.

- :mod:`handlers.interfaces.o1`   — O1 cell configuration via SDNC REST
- :mod:`handlers.interfaces.a1`   — A1 policy management
- :mod:`handlers.interfaces.e2`   — E2SM-KPM subscribe + E2SM-RC control
- :mod:`handlers.interfaces.r1`   — R1 SME lifecycle + ICS data subscription
- :mod:`handlers.interfaces.teiv` — TEIV topology discovery
- :mod:`handlers.interfaces.ves`  — inbound O1 VES events
"""
