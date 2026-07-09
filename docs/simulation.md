# Simulation Guide

Simulation for rApps and xApps built from this template is orchestrated by
the **BMW Lab TA rApp** — a dedicated test automation component that controls
the simulator lifecycle and validates O-RAN interfaces.

The generic rApp / xApp uses `RAPP_PLATFORM=osc` pointed at the simulator's
O-RAN interfaces.  It never calls simulator APIs directly.

---

## Architecture

```
[VIAVI RSG / ns-3]
    ├── O1 (NETCONF) ────────────────► SMO / SDNC
    ├── A1 (via Non-RT RIC) ─────────► your rApp (A1Port)
    ├── E2 (KPM / RC) ───────────────► your xApp (E2KpmPort / E2RcPort)
    └── Proprietary REST API ────────► TA rApp (start / stop simulation)

[TA rApp]
    ├── Controls VIAVI RSG via REST (`/sba/tests/run`)
    ├── Validates O1 / A1 / E2 interface connectivity
    ├── Deploys your rApp / xApp under test
    ├── Collects PM data from InfluxDB
    └── Compares pre-app vs post-app KPIs → test report

[Your rApp / xApp]
    └── Talks only through O-RAN protocols (O1 / A1 / R1 / E2)
        — identical to production deployment
```

---

## Requirements

| Component | Version | Purpose |
| --- | --- | --- |
| BMW Lab TA rApp | latest `master` | Simulation orchestration |
| VIAVI RSG | — | O-RAN network simulator |
| O-RAN SC Non-RT RIC | L Release | SME / ICS / A1PMS endpoints |
| Kubernetes | 1.28+ | Runtime for TA rApp and your rApp |
| Helm | v3 | Chart deployment |

TA rApp repository: <https://github.com/bmw-ece-ntust/nonrtric-rapp-test-automation>

---

## Setup

### 1. Deploy the TA rApp

Follow the TA rApp user guide (see its `README.md`):

```bash
git clone https://github.com/bmw-ece-ntust/nonrtric-rapp-test-automation.git
cd nonrtric-rapp-test-automation/Test-Automation-rApp
sudo nerdctl build -t joechang1030/ta-rapp:1.0.0 .
helm install ta-rapp ./   # follow TA rApp Helm instructions
```

### 2. Deploy your rApp / xApp

Use the Helm chart from `helm/template-app/`:

```bash
# Set values for your deployment
helm install my-rapp helm/template-app \
  --set image.repository=<your-registry/rapp> \
  --set image.tag=latest \
  --set env.RAPP_PLATFORM=osc \
  --set env.RAPP_SME_BASE_URL=http://nonrtric:8090 \
  --set env.RAPP_ICS_BASE_URL=http://nonrtric:8083 \
  --set env.RAPP_CALLBACK_URL=http://<pod-ip>:8080/r1/callback \
  --set env.RAPP_CELL_ID=o-du-1111/cell-0
```

Your rApp registers with SME and subscribes to ICS on startup automatically
(`OscLifecycleRunner.start()`).

### 3. Upload a test specification to the TA rApp

```bash
curl -X POST http://<ta-rapp-svc>:8080/upload_test_spec \
  -H "Content-Type: application/json" \
  -d @<path-to-test-spec.json>
```

The TA rApp then:
1. Generates VIAVI RSG configuration from the test spec.
2. Runs **Phase 1** — simulation without your rApp (baseline KPIs).
3. Validates O1 / A1 / E2 interface connectivity.
4. Deploys your rApp / xApp via A1 policy.
5. Runs **Phase 2** — simulation with your rApp active.
6. Compares Phase 1 vs Phase 2 KPIs and writes the test report to InfluxDB.

---

## Local unit testing (no TA rApp required)

Drive any analyzer with canned data — analyzers are pure classes, and
`tests/conftest.FakeTelemetryCollector` stands in for the network:

```bash
PYTHONPATH=src python -m examples.threshold_energy_saving_rapp
```

Or in pytest:

```python
from conftest import FakeTelemetryCollector
from factories.osc import OscKpiAnalyzer

collector = FakeTelemetryCollector({"DRB.PrbUtilDL": 0.85})
analyzer  = OscKpiAnalyzer("cell-0")
report    = analyzer.analyze(collector.collect())
assert report.prb_util_dl == 0.85
```

This requires zero external dependencies and covers the full optimization
logic path (`TelemetryCollector → KpiAnalyzer → OptimizationStrategy → PolicyDecision`).

---

## ns-3 simulation

The TA rApp currently supports VIAVI RSG.  For ns-3, two options exist:

| Option | Description |
| --- | --- |
| **ns-O-RAN** | ns-3 with built-in E2 node; your xApp connects directly via standard E2. Use `RAPP_PLATFORM=osc` pointed at ns-O-RAN Near-RT RIC. Reference: <https://openrangym.com/ran-frameworks/ns-o-ran> |
| **TA rApp ns-3 controller** | Extend the TA rApp with an ns-3 `ScenarioController` (parallel to `rictest_controller.py`). Your rApp code is unchanged. |

In both cases the rApp / xApp uses O-RAN protocols only — no ns-3 API calls.

---

## Links

- [TA rApp repository](https://github.com/bmw-ece-ntust/nonrtric-rapp-test-automation)
- [Docker + Helm deployment](continerized.md)
- [User guide](USER-GUIDE.md)
- [CONTEXT.md — architecture and O-RAN interface reference](../CONTEXT.md)
