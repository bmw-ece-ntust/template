# src/

Runnable rApp/xApp source. The entrypoint is `main.py`; Python runtime deps are
in `requirements.txt` (O-RAN SC `nonrtric-rapp-healthcheck` convention).

## Layout (MVC + handlers, inspired by OSC `ric-app-kpimon-go`)

`ric-app-kpimon-go` — the cleanest OSC xApp — is essentially *entry point +
controller + protocol handlers + models*. This template follows the same shape,
adding a typed/tested/documented structure:

One top-level class per module (SOP programming.md Section 5.1): packages
below list their classes; each class lives in its own `snake_case` file and
the package `__init__.py` only re-exports.

```text
main.py          Composition root: RAPP_PLATFORM → factory table, control loop, HTTP
models/          M — data only, no I/O
  kpi/             KpiReport (+ from_3gpp), PolicyDecision
  parameters/      ThreeGPPKpi, NodeType, VendorParameterMap
  topology/        NodeInfo, NetworkTopology
  intent/          IntentContract, IntentType, IntentResolutionService, …
  health.py        Health
controllers/     C — orchestration + algorithms
  kpi_controller.py  KpiController: collect → analyze → decide
  health.py          HealthService + get_health_payload
  strategies/        OptimizationStrategy (Threshold / EnergySaving / ML / Nvidia)  ← Strategy pattern
handlers/        O-RAN STANDARD interfaces only  ← Adapter pattern
  interfaces/      a1/ e2/ o1/ r1/ teiv/ ves/
factories/       osc (3GPP) + ns3 / viavi / oai / ocudu  ← Abstract Factory
                 vendor packages: params.py (enum + map), kpi_analyzer.py (Adapter), factory.py
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
