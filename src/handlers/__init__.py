"""Handlers — the O-RAN standard interface boundary (Adapter pattern).

This package contains **only** adapters that speak published O-RAN ALLIANCE /
3GPP protocols.  Nothing proprietary lives here: vendor-specific telemetry
translation is a deployment concern handled by the per-vendor platform
factories under :mod:`factories` (e.g. :mod:`factories.viavi`), selected via
``RAPP_PLATFORM``.

Standard O-RAN interface adapters live in :mod:`handlers.interfaces`.
"""
