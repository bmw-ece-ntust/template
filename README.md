# O-RAN rApp / xApp Template — Getting Started & User Guide

BMW Lab (NTUST ECE) starter template for O-RAN Non-RT RIC **rApps** and
Near-RT RIC **xApps**. Simple, professional **MVC + handlers** structure
(models / controllers / views, with O-RAN I/O in handlers — the shape of OSC
`ric-app-kpimon-go`), O-RAN ALLIANCE protocol adapters (O1/A1/R1/E2),
multi-vendor parameter normalization, spec-traceable 3GPP KPIs, and pluggable
deployment factories.

> **Full PRD:** [CONTEXT.md](CONTEXT.md) · **Architecture rules:** [CLAUDE.md](CLAUDE.md)
> · **Generate a new rApp with an LLM:** [docs/llm-authoring-guide.md](docs/llm-authoring-guide.md)

---

## What you get

| Capability | Where |
| --- | --- |
| MVC layers (models / controllers / views) | `src/models/`, `src/controllers/`, `src/views/` |
| O-RAN standard interface adapters (O1/A1/E2/R1/TEIV/VES) | `src/handlers/interfaces/` |
| Multi-vendor proprietary factories (Ericsson, Nokia) | `src/factories/<vendor>/` |
| Spec-traceable 3GPP KPI enum | `src/models/parameters.py` (`ThreeGPPKpi`) |
| Strategy / Abstract-Factory / Adapter patterns | `controllers/strategies.py`, `factories/`, `handlers/interfaces/` |
| Contract-based Intent (IBN) with HMAC validation | `src/models/intent.py` |
| Tests (pytest, 80% gate on models+controllers) | `tests/` |
| Lint + type + format + CI | `pyproject.toml`, `.github/workflows/ci.yml` |
| Sphinx API docs | `docs/conf.py` |
| Hardened Helm chart | `helm/template-app/` |
| Runnable examples | `examples/` |

---

## Quick Start

```bash
git clone https://github.com/bmw-ece-ntust/nonrtric-rapp-template.git
cd nonrtric-rapp-template

# Run with the mock platform (no external dependencies)
pip install -r src/requirements.txt
RAPP_PLATFORM=mock PYTHONPATH=src python src/main.py
# then: curl http://localhost:8080/health
```

```bash
# Run against a live Non-RT RIC (or the VIAVI TA rApp O-RAN endpoints)
export RAPP_PLATFORM=osc
export RAPP_SME_BASE_URL=http://nonrtric:8090
export RAPP_ICS_BASE_URL=http://nonrtric:8083
export RAPP_CALLBACK_URL=http://<this-pod-ip>:8080/r1/callback
export RAPP_INTENT_SECRET=$(openssl rand -hex 32)
PYTHONPATH=src python src/main.py
```

```bash
# Docker
docker build -t rapp-template:latest .
docker run -p 8080:8080 -e RAPP_PLATFORM=mock rapp-template:latest
```

```bash
# Helm (Kubernetes). Provide the intent secret at install time.
helm install my-rapp helm/template-app \
  --set secrets.RAPP_INTENT_SECRET=$(openssl rand -hex 32)
```

---

## Try the examples

Network-free demos of the core data flow:

```bash
PYTHONPATH=src python -m examples.threshold_energy_saving_rapp   # telemetry → strategy → A1 payload
PYTHONPATH=src python -m examples.vendor_ericsson_adapter        # proprietary → ThreeGPPKpi → KpiReport
PYTHONPATH=src python -m examples.intent_resolution             # signed intent contract validation
```

---

## Configuration

All configuration is read from environment variables at startup. Copy
[config/.env.example](config/.env.example) to `.env` and fill in values; never
commit `.env`. In Kubernetes these map to the chart's `config:` (ConfigMap) and
`secrets:` (Secret) values.

| Env var | Default | Description |
| --- | --- | --- |
| `RAPP_PLATFORM` | `mock` | `mock` / `osc` / `physical` / `ericsson` / `nokia` |
| `RAPP_STRATEGY` | `threshold` | Optimization algorithm (`make_strategy`) |
| `RAPP_HOST` | `0.0.0.0` | Bind address |
| `RAPP_PORT` | `8080` | Listen port |
| `RAPP_SERVICE_NAME` | `template-app` | Service name in health payload |
| `RAPP_SME_BASE_URL` | — | Non-RT RIC SME base URL (osc only) |
| `RAPP_ICS_BASE_URL` | — | Non-RT RIC ICS base URL (osc only) |
| `RAPP_EMS_BASE_URL` | — | Vendor EMS/NMS base URL (`ericsson` / `nokia` only) |
| `RAPP_CALLBACK_URL` | — | This rApp's inbound callback URL (osc only) |
| `RAPP_CELL_ID` | `cell-0` | Primary cell ID (osc only) |
| `RAPP_INTENT_SECRET` | — | HMAC secret for IBN intent contracts |

---

## HTTP Endpoints

| Path | Method | Response |
| --- | --- | --- |
| `/` `/health` `/status` | GET | JSON health payload |
| `/stats` | GET | HTML stats page (auto-refresh 5 s) |

These are operational endpoints only. O-RAN traffic flows over O1/A1/E2/R1, not HTTP.

---

## Deployment Platforms

| `RAPP_PLATFORM` | Description | Use when |
| --- | --- | --- |
| `mock` | In-memory no-op, fixed KPI fixture | Unit tests, demos, CI, developer laptop |
| `osc` | Live O-RAN interfaces via ICS/SME (telemetry already in 3GPP names) | Production OSC deployment or VIAVI simulation via the BMW Lab TA rApp |
| `physical` | Physical gNB testbed | Real hardware experiments |
| `ericsson` | Ericsson EMS/ENM management plane; proprietary PM → `ThreeGPPKpi` Adapter | Reading an Ericsson node's proprietary counters directly |
| `nokia` | Nokia NetAct management plane; proprietary PM → `ThreeGPPKpi` Adapter | Reading a Nokia node's proprietary counters directly |

**Simulation note:** Simulator lifecycle (start/stop VIAVI or ns-3 scenarios, UE
mobility) is the responsibility of the BMW Lab TA rApp
([nonrtric-rapp-test-automation](https://github.com/bmw-ece-ntust/nonrtric-rapp-test-automation)).
Use `RAPP_PLATFORM=osc` pointed at the TA rApp O-RAN endpoints; the generic rApp
never calls simulator APIs directly.

---

## Author a new rApp

This repo is a **template**, not an app you edit in place. Start a new rApp by
**copying and renaming**, so the template stays reusable and your product stays
clean.

### 1. Copy and rename

```bash
# Copy the template to a new repo and rename the app
cp -r template my-energy-saving-rapp && cd my-energy-saving-rapp
git grep -l 'template-app' | xargs sed -i '' 's/template-app/energy-saving-rapp/g'   # macOS sed
# also set RAPP_SERVICE_NAME, helm Chart.yaml name, and the image repository
```

### 2. Prune the examples you don't need

The template ships illustrative pieces. Keep what your PRD needs; delete the rest
so nothing misleads a reader (or an LLM):

| Building an… | Keep | Can delete |
| --- | --- | --- |
| **rApp** (Non-RT RIC) | `handlers/interfaces/{o1,a1,r1,teiv,ves}.py`, `factories/osc` | `handlers/interfaces/e2.py` (that is the xApp path) |
| **xApp** (Near-RT RIC) | `handlers/interfaces/e2.py` | `handlers/interfaces/{r1,teiv}.py` if unused |
| single vendor | one `factories/<vendor>/` | the other vendor example |
| one algorithm | your `controllers/strategies.py` class | the strategy variants you don't use |

> **rApp vs xApp:** an rApp emits **A1 policy** (or **O1** config) and lets the
> Near-RT RIC do E2 control. Do not wire `E2SmRcAdapter` into an rApp.
>
> **"From O-RAN WG1":** WG1 publishes *use-case specifications* (e.g. Network
> Energy Saving), not an interface. Realize the use case over R1 (telemetry) +
> A1/O1 (action). The A1 example in `handlers/interfaces/a1.py` is a *Traffic Steering*
> policy — for Energy Saving, define your own policy type / decision data,
> don't reuse the `ORAN_TrafficSteering_0.1.0` schema verbatim.

### 3. Fill the PRD and generate

1. Copy [docs/PRD-TEMPLATE.md](docs/PRD-TEMPLATE.md) into `CONTEXT.md` and fill it in.
2. Follow [docs/llm-authoring-guide.md](docs/llm-authoring-guide.md): write the
   `controllers/strategies.py` algorithm first, reuse the `handlers/interfaces/`
   adapters, add `factories/<vendor>/` only if you need a new vendor, compose in
   `main.py`, add tests.
3. Run the Definition-of-Done checks below.

---

## Develop

```bash
pip install -e ".[dev,docs]"      # tooling: ruff, mypy, pytest, sphinx

ruff check src tests examples      # lint
ruff format --check src tests examples
mypy src                           # type check
pytest                             # tests + 80% coverage gate (core + domain)
sphinx-build -b html docs docs/_build/html -W   # API docs
helm lint helm/template-app        # chart
graphify update .                  # refresh the knowledge graph (free, AST-only)
```

CI runs the same gates on every push/PR ([.github/workflows/ci.yml](.github/workflows/ci.yml)).

### Knowledge graph (graphify)

This repo ships a queryable code graph so Claude Code explores it cheaply.

```bash
/graphify .          # first build (code-only is free)
graphify update .    # AST refresh after edits, no LLM cost
graphify query "How does the rApp send an A1 policy?"
```

Read `graphify-out/GRAPH_REPORT.md` before opening raw source. See
[docs/osc-reference-study.md](docs/osc-reference-study.md) for how this
template's structure compares to OSC reference apps.

---

## Known Issues

| Issue | Severity | Status | Workaround |
| --- | --- | --- | --- |
| E2 transport is a stub (no RMR/gRPC) | ℹ INFO | Pending | Use `mock`; implement `E2Client` ABC with `ricxappframe` RMR for your RIC |
| VES push receiver not wired to HTTP server | ℹ INFO | Pending | ICS polling via `OscIcsTelemetryCollector` works as fallback |
| `PhysicalPlatformFactory` raises `NotImplementedError` | ℹ INFO | Pending | Use `osc` for real deployments |
| `IntentResolutionService.resolve()` raises `NotImplementedError` | ℹ INFO | Pending | Implement intent → PolicyDecision logic per use case |
| Vendor proprietary maps are illustrative | ⚠ WARN | Open | Validate Ericsson/Nokia counter names against vendor PM references before production |

---

## Directory Layout

```text
pyproject.toml                     Project metadata + ruff/mypy/pytest config
tests/                             pytest suite (models, controllers, adapters)
examples/                          Runnable end-to-end demos
helm/template-app/                 Hardened Helm chart (configmap, secret, SA)
docs/                              Sphinx config + guides (PRD, authoring, SOP review)
src/
├── main.py                        Composition root; RAPP_PLATFORM routing + control cycle
├── requirements.txt               Runtime deps (requests>=2.32)
├── models/                        M — kpi, parameters, topology, intent, health
├── controllers/                   C — kpi_controller, health, strategies
├── handlers/                      O-RAN standard interfaces only
│   └── interfaces/                a1 e2 o1 r1 teiv ves
├── factories/                     Abstract Factory: mock / osc / physical + ericsson / nokia
├── views/                         V — http (health/stats) + grafana dashboards
└── config/                        settings.py (RAPP_* env vars) + logging.py
```

---

## Links

- [CONTEXT.md](CONTEXT.md) — Full PRD (architecture, MSC, class diagram, parameters)
- [docs/PRD-TEMPLATE.md](docs/PRD-TEMPLATE.md) — Fill-in PRD for a new rApp
- [docs/llm-authoring-guide.md](docs/llm-authoring-guide.md) — PRD → rApp workflow
- [docs/osc-reference-study.md](docs/osc-reference-study.md) — OSC reference-app survey
- [docs/sop-review.md](docs/sop-review.md) — BMW Lab SOP assessment
- [docs/simulation.md](docs/simulation.md) — Simulation via the TA rApp
- [helm/template-app/](helm/template-app/) — Kubernetes Helm chart
- [BMW Lab SOP](https://github.com/bmw-ece-ntust/SOP) · [BMW Lab TA rApp](https://github.com/bmw-ece-ntust/nonrtric-rapp-test-automation)
