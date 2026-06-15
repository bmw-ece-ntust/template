"""Views (V) — how this rApp/xApp surfaces state to operators.

- :mod:`views.http` — operational health/stats HTTP endpoints.
- ``views/grafana/`` — Grafana dashboard JSON for the SMO. The app writes
  KPIs/decisions to the SMO metrics store (InfluxDB/Prometheus via ICS); Grafana
  renders them. Views carry no business logic.
"""
