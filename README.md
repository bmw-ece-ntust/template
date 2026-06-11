# rApp / xApp Template — User Guide

BMW Lab (NTUST ECE) research template for O-RAN Non-RT RIC rApps and
Near-RT RIC xApps.  Implements clean hexagonal architecture with O-RAN
ALLIANCE protocol adapters (O1/A1/R1/E2) and pluggable deployment factories.

> **Full project documentation (PRD):** See [CONTEXT.md](CONTEXT.md)
> **Architecture rules for Claude Code:** See [CLAUDE.md](CLAUDE.md)

---

## Vibe-Coding with Claude Code

This repo is a **vibe-coding template**: it ships pre-configured for
AI-assisted development with Claude Code, tuned to keep token consumption low
while exploring an O-RAN hexagonal-architecture codebase.

### Knowledge graph (`graphify`)

Instead of having Claude read every source file to understand the codebase,
this template uses the [`graphify`](https://github.com/safishamsi/graphify)
`/graphify` skill to maintain a queryable knowledge graph at `graphify-out/`.

```bash
# One-time global setup (already done if you're reading this in a configured environment)
uv tool install graphifyy
graphify install

# Build or refresh the graph for this project
/graphify .          # first build
graphify update .    # AST-only refresh after code edits, no LLM cost
```

This produces:

- `graphify-out/GRAPH_REPORT.md` — plain-language architecture overview, "god
  nodes", and community structure. Read this **before** opening raw source
  files.
- `graphify-out/graph.json` — structured graph for `graphify query`,
  `graphify path`, and `graphify explain`.
- `graphify-out/wiki/` (optional) — agent-crawlable per-module pages.

```bash
graphify query "How does the rApp send an A1 policy?"
graphify path "OscPlatformFactory" "A1Adapter"
graphify explain "IntentResolutionService"
```

`.graphifyignore` already excludes `.venv/`, `__pycache__/`,
`helm/**/charts/`, and other non-essential paths from the graph. See
[CLAUDE.md](CLAUDE.md#knowledge-graph-graphify) for the session rules Claude
follows when using the graph.

---

## Quick Start

```bash
# Clone and run with mock platform (no external dependencies)
git clone https://github.com/bmw-ece-ntust/nonrtric-rapp-template.git
cd nonrtric-rapp-template
pip install -r src/requirements.txt
RAPP_PLATFORM=mock python src/main.py
```

```bash
# Run against O-RAN SC Non-RT RIC (or VIAVI TA rApp endpoint)
export RAPP_PLATFORM=osc
export RAPP_SME_BASE_URL=http://nonrtric:8090
export RAPP_ICS_BASE_URL=http://nonrtric:8083
export RAPP_CALLBACK_URL=http://<this-pod-ip>:8080/r1/callback
python src/main.py
```

```bash
# Docker
docker build -t rapp-template:latest .
docker run -p 8080:8080 -e RAPP_PLATFORM=mock rapp-template:latest
```

```bash
# Helm (Kubernetes)
helm install my-rapp helm/template-app
```

---

## Configuration

All configuration is read from environment variables at startup.  Copy
[config/.env.example](config/.env.example) to `.env` and fill in values.
Never commit `.env`.

| Env var | Default | Description |
| --- | --- | --- |
| `RAPP_PLATFORM` | `mock` | `mock` / `osc` / `physical` |
| `RAPP_HOST` | `0.0.0.0` | Bind address |
| `RAPP_PORT` | `8080` | Listen port |
| `RAPP_SERVICE_NAME` | `template-app` | Service name in health payload |
| `RAPP_SME_BASE_URL` | — | Non-RT RIC SME base URL (osc only) |
| `RAPP_ICS_BASE_URL` | — | Non-RT RIC ICS base URL (osc only) |
| `RAPP_CALLBACK_URL` | — | This rApp's inbound callback URL (osc only) |
| `RAPP_CELL_ID` | `cell-0` | Primary cell ID (osc only) |
| `RAPP_INTENT_SECRET` | — | HMAC secret for IBN intent contracts |

---

## HTTP Endpoints

| Path | Method | Response |
| --- | --- | --- |
| `/` `/health` `/status` | GET | JSON health payload |
| `/stats` | GET | HTML stats page (auto-refresh 5 s) |

---

## Deployment Platforms

| `RAPP_PLATFORM` | Description | Use when |
| --- | --- | --- |
| `mock` | In-memory no-op, fixed KPI fixture | Unit tests, demos, CI, developer laptop |
| `osc` | Live O-RAN interfaces via ICS/SME | Production OSC deployment or VIAVI simulation via BMW Lab TA rApp |
| `physical` | Physical gNB testbed | Real hardware experiments |

**Simulation note:** Simulator lifecycle (start/stop VIAVI or ns-3 scenarios,
configure UE mobility) is the responsibility of the BMW Lab TA rApp
([nonrtric-rapp-test-automation](https://github.com/bmw-ece-ntust/nonrtric-rapp-test-automation)).
Use `RAPP_PLATFORM=osc` pointed at the TA rApp O-RAN endpoints — the generic
rApp never calls simulator APIs directly.

---

## Known Issues

| Issue | Severity | Status | Workaround |
| --- | --- | --- | --- |
| E2 adapter is a stub | ⚠ INFO | Pending | Use `mock` platform; implement `E2Client` ABC for your RIC |
| VES push receiver not wired to HTTP server | ⚠ INFO | Pending | ICS polling via `OscIcsTelemetryCollector` works as fallback |
| `PhysicalPlatformFactory` raises `NotImplementedError` | ⚠ INFO | Pending | Use `osc` platform for real deployments |
| `IntentResolutionService.resolve()` raises `NotImplementedError` | ⚠ INFO | Pending | Implement intent → PolicyDecision logic for your use case |

---

## Directory Layout

```text
src/
├── main.py                    Composition root; RAPP_PLATFORM factory routing
├── requirements.txt           Runtime deps (requests>=2.32)
├── core/
│   ├── models/
│   │   ├── __init__.py        KpiReport (3GPP TS 28.552), PolicyDecision
│   │   └── parameters.py      ThreeGPPKpi enum, NodeType enum, VendorParameterMap
│   └── strategies/            OptimizationStrategy ABC, Threshold/ML/NvidiaModel variants
├── factories/
│   ├── __init__.py            RAppPlatformFactory ABC, ScenarioRunner/Collector/Analyzer ABCs
│   ├── mock/                  MockPlatformFactory (in-memory, no deps)
│   ├── osc/                   OscPlatformFactory (ICS + SME)
│   └── physical/              PhysicalPlatformFactory stub
└── rapp/
    ├── adapters/
    │   ├── a1/                A1Adapter → ORAN_TrafficSteering A1 policy
    │   ├── e2/                E2SmKpmAdapter + E2SmRcAdapter stubs
    │   ├── http/              HTTP server (health + stats endpoints only)
    │   ├── o1/                O1SdncAdapter → SDNC REST → NETCONF → gNB
    │   ├── r1/                SMEAdapter + ICSAdapter
    │   ├── teiv/              TEIVAdapter → NetworkTopology
    │   ├── ves/               VesEventAdapter (inbound O1 VES events)
    │   └── vendor/            GnbTelemetryAdapter (vendor → 3GPP KPIs)
    ├── application/
    │   ├── ports.py           Port Protocols: Health/O1/R1/A1/E2/Intent/VES/Topology
    │   └── usecases.py        get_health_payload()
    ├── config/settings.py     Settings dataclass (RAPP_* env vars)
    ├── domain/
    │   ├── intent.py          IntentContract, IntentType whitelist, IntentResolutionService
    │   ├── models.py          Health frozen dataclass
    │   ├── services.py        HealthService
    │   └── topology.py        NodeInfo, NetworkTopology
    └── infrastructure/
        └── logging.py         configure_logging()
```

---

## Links

- [CONTEXT.md](CONTEXT.md) — Full PRD (architecture, MSC, class diagram, system parameters)
- [docs/USER-GUIDE.md](docs/USER-GUIDE.md) — End-user operating instructions
- [docs/simulation.md](docs/simulation.md) — Simulation guide (TA rApp setup + test flow)
- [docs/continerized.md](docs/continerized.md) — Docker + Helm deployment tutorial
- [helm/template-app/](helm/template-app/) — Helm chart for Kubernetes deployment
- [config/.env.example](config/.env.example) — All env vars with annotations
- [BMW Lab SOP](https://github.com/bmw-ece-ntust/SOP) — Source code and documentation standards
- [BMW Lab TA rApp](https://github.com/bmw-ece-ntust/nonrtric-rapp-test-automation) — Simulation orchestration
