# src/

Runnable rApp/xApp source. The entrypoint is `main.py`; Python runtime deps are
in `requirements.txt` (O-RAN SC `nonrtric-rapp-healthcheck` convention).

## Layout (MVC + handlers, inspired by OSC `ric-app-kpimon-go`)

`ric-app-kpimon-go` — the cleanest OSC xApp — is essentially *entry point +
controller + protocol handlers + models*. This template follows the same shape,
adding a typed/tested/documented structure:

```text
main.py          Composition root: select platform factory, run control loop, serve HTTP
models/          M — data only, no I/O
  kpi.py           KpiReport, PolicyDecision, KpiReport.from_3gpp
  parameters.py    ThreeGPPKpi, NodeType, VendorParameterMap
  topology.py      NodeInfo, NetworkTopology
  intent.py        IntentContract, IntentType, IntentResolutionService
  health.py        Health
controllers/     C — orchestration + algorithms
  kpi_controller.py  KpiController: collect → analyze → decide
  health.py          HealthService + get_health_payload
  strategies.py      OptimizationStrategy (Threshold / ML / Nvidia)  ← Strategy pattern
handlers/        O-RAN + vendor I/O boundary  ← Adapter pattern
  a1.py e2.py o1.py r1.py teiv.py ves.py vendor.py
  adapters/        proprietary per-vendor: ericsson/ nokia/
factories/       mock / osc / physical component creators  ← Abstract Factory
views/           V — how state is surfaced
  http/            health/stats HTTP endpoints
  grafana/         dashboard JSON for the SMO Grafana
config/          settings.py (env vars) + logging.py
```

## Dependency direction

`models` depends on nothing. `controllers` depend on `models` (and on the
`factories` ABCs for typing). `handlers` and `factories` depend on `models`.
`views` depend on `controllers`. `main.py` wires it all together. No business
logic imports HTTP/REST libraries directly — that lives in `handlers`/`views`.
