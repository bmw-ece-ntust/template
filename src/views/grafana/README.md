# Views — Grafana (the "V" in MVC)

In the O-RAN SMO, visualization is **not** code inside the rApp. Following the
pattern of OSC xApps such as `ric-app-kpimon-go` (which writes metrics to a DB
and lets Grafana render them), the view layer here is a **Grafana dashboard
definition**, not a Python module.

## Data flow

```
gNB --(O1 VES / E2 KPM)--> SMO ranpm pipeline --> InfluxDB/Prometheus --> Grafana
rApp --(writes its own decisions/KPIs)--------> SMO metrics store ------> Grafana
```

- 3GPP PM counters (`DRB.PrbUtilDL`, `RRC.ConnMean`, …) reach the SMO metrics
  store through the standard ranpm / ICS pipeline. The rApp consumes them via
  ICS (it does **not** query InfluxDB directly — see Architectural Rule 2).
- The rApp's own outputs (the `PolicyDecision` per cell) are written to a
  measurement (e.g. `rapp_policy`) so operators can see what the rApp did.

## Using the starter dashboard

1. In Grafana: **Dashboards → Import → Upload JSON** and select
   [`rapp-kpi-dashboard.json`](rapp-kpi-dashboard.json).
2. When prompted, bind the `DS_SMO` input to your SMO datasource (InfluxDB by
   default; adapt the queries for Prometheus/PromQL if that is your backend).
3. The `cell_id` template variable filters all panels per cell.

Panels: DL PRB utilization, active UEs, and the rApp policy-decision timeline.
Treat this as a starting point and extend it with the KPIs your rApp emits.
