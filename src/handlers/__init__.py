"""Handlers — the O-RAN and vendor I/O boundary (Adapter pattern).

Standard O-RAN interface adapters live directly in this package:

- :mod:`handlers.o1`   — O1 cell configuration via SDNC REST
- :mod:`handlers.a1`   — A1 policy management
- :mod:`handlers.e2`   — E2SM-KPM subscribe + E2SM-RC control
- :mod:`handlers.r1`   — R1 SME lifecycle + ICS data subscription
- :mod:`handlers.teiv` — TEIV topology discovery
- :mod:`handlers.ves`  — inbound O1 VES events
- :mod:`handlers.vendor` — generic vendor telemetry ABC

Proprietary, per-vendor adapters live under :mod:`handlers.adapters`.
"""
