# CLAUDE.md — Static Knowledge Snapshot

> **Purpose:** This file is a static knowledge snapshot for LLMs.
> It describes the repository structure, conventions, terminology, and
> external links as of the last update.  Do **not** log session activity
> or prompting history here.

---

## Project Overview

This repository is a **research rApp template** that follows the
[O-RAN SC `nonrtric-rapp-healthcheck`](https://gerrit.o-ran-sc.org/r/admin/repos/nonrtric/plt/rappmanager)
layout.  It provides a minimal, runnable skeleton for BMW Lab (NTUST ECE)
research projects that target the O-RAN Non-RT RIC platform.

The application wires a small **Clean / Hexagonal Architecture** under
`src/rapp/`, and ships platform-agnostic design-pattern stubs
(`src/core/`, `src/factories/`) so research extensions can be bolted on
without touching the core transport layer.

---

## Repository Layout

```
template/
├── CLAUDE.md                          ← this file
├── Dockerfile                         ← multi-stage Python 3.12-slim image; WORKDIR /src
├── README.md                          ← SOP project-documentation template guide
├── config/
│   └── .env.example                   ← annotated env-var reference (copy → .env)
├── docs/
│   ├── README.md                      ← doc-structure overview
│   ├── USER-GUIDE.md                  ← end-user operating instructions
│   ├── continerized.md                ← Docker + Helm deployment tutorial
│   ├── api/
│   │   └── .gitkeep                   ← placeholder: OpenAPI / AsyncAPI specs go here
│   ├── drawio/
│   │   └── .gitkeep                   ← placeholder: architecture draw.io diagrams
│   └── upstream/
│       └── sync_sop_project_documentation.sh  ← script that syncs SOP upstream docs
├── simulation/
│   └── .gitkeep                       ← placeholder: ns-3 / VIAVI scenario scripts
├── src/
│   ├── main.py                        ← composition root; wires all layers; CLI entry
│   ├── requirements.txt               ← runtime deps (empty by default — stdlib only)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   └── __init__.py            ← KpiReport (3GPP TS 28.552), PolicyDecision enum
│   │   └── strategies/
│   │       └── __init__.py            ← OptimizationStrategy ABC, ThresholdBasedStrategy, MlBasedStrategy
│   ├── factories/
│   │   ├── __init__.py                ← RAppPlatformFactory ABC + ScenarioRunner / TelemetryCollector / KpiAnalyzer ABCs
│   │   ├── ns3/
│   │   │   └── __init__.py            ← Ns3PlatformFactory (ns-3 simulation)
│   │   ├── viavi/
│   │   │   └── __init__.py            ← ViaviPlatformFactory (VIAVI RSG test equipment)
│   │   └── physical/
│   │       └── __init__.py            ← PhysicalPlatformFactory (real gNB testbed)
│   └── rapp/
│       ├── __init__.py
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── http/
│       │   │   ├── __init__.py
│       │   │   ├── api.py             ← HTTP request handler; routes /, /health, /status, /stats
│       │   │   └── server.py          ← HTTPServer wrapper; serve_http() blocking call
│       │   └── vendor/
│       │       └── __init__.py        ← GnbTelemetryAdapter + VendorTelemetryClient ABC
│       ├── application/
│       │   ├── __init__.py
│       │   ├── ports.py               ← HealthPort Protocol (structural typing)
│       │   └── usecases.py            ← get_health_payload() use-case function
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py            ← Settings dataclass; reads RAPP_* env vars (+ legacy names)
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── models.py              ← Health frozen dataclass
│       │   └── services.py            ← HealthService (domain service, transport-free)
│       └── infrastructure/
│           ├── __init__.py
│           └── logging.py             ← configure_logging(); basicConfig with timestamp + level
└── test/
    ├── README.md
    ├── start.sh                       ← deploy the Helm chart to the local cluster
    ├── stop.sh                        ← tear down the Helm release
    └── usecases/
        └── healthcheck/
            └── scriptversion/
                └── helm/
                    └── template-app/
                        ├── Chart.yaml         ← chart name: template-app, version: 0.1.0
                        ├── values.yaml
                        └── templates/
                            ├── _helpers.tpl
                            ├── deployment.yaml
                            ├── service.yaml
                            └── NOTES.txt
```

---

## Architecture

### Layer responsibilities

| Layer | Package | Rule |
|---|---|---|
| **Domain** | `src/rapp/domain/` | Pure business logic; no I/O, no frameworks |
| **Application** | `src/rapp/application/` | Use-cases; depends only on domain + ports |
| **Adapters** | `src/rapp/adapters/` | HTTP transport, vendor telemetry wrappers |
| **Config** | `src/rapp/config/` | Settings read from env vars at startup |
| **Infrastructure** | `src/rapp/infrastructure/` | Cross-cutting concerns (logging) |
| **Core** | `src/core/` | Platform-agnostic data models and strategy ABCs |
| **Factories** | `src/factories/` | Platform-specific component creators (Abstract Factory) |

### Design patterns in use

| Pattern | Location | Reference |
|---|---|---|
| Hexagonal / Ports-and-Adapters | `rapp/application/ports.py` + `rapp/adapters/` | — |
| **Adapter** | `src/rapp/adapters/vendor/__init__.py` | [refactoring.guru/adapter](https://refactoring.guru/design-patterns/adapter) |
| **Abstract Factory** | `src/factories/__init__.py` + `ns3/`, `viavi/`, `physical/` | [refactoring.guru/abstract-factory](https://refactoring.guru/design-patterns/abstract-factory) |
| **Strategy** | `src/core/strategies/__init__.py` | [refactoring.guru/strategy](https://refactoring.guru/design-patterns/strategy) |

---

## Key Classes and Entry Points

| Symbol | File | Notes |
|---|---|---|
| `main()` | `src/main.py` | Composition root; wires all layers; CLI via `argparse` |
| `Settings` | `src/rapp/config/settings.py` | Frozen dataclass; env vars: `RAPP_HOST`, `RAPP_PORT`, `RAPP_SERVICE_NAME` |
| `Health` | `src/rapp/domain/models.py` | Frozen dataclass: `status`, `service`, `timestamp` |
| `HealthService` | `src/rapp/domain/services.py` | Returns `Health(status="OK", ...)` with current Unix time |
| `HealthPort` | `src/rapp/application/ports.py` | `Protocol` satisfied by any class with `get_health()` |
| `get_health_payload()` | `src/rapp/application/usecases.py` | Returns JSON-serializable dict |
| `make_handler()` | `src/rapp/adapters/http/api.py` | Factory returning `BaseHTTPRequestHandler` subclass |
| `serve_http()` | `src/rapp/adapters/http/server.py` | Blocking `HTTPServer.serve_forever()` |
| `KpiReport` | `src/core/models/__init__.py` | Frozen dataclass; 3GPP TS 28.552-linked fields |
| `PolicyDecision` | `src/core/models/__init__.py` | Enum: `ACTIVE`, `SLEEP`, `HANDOVER` |
| `OptimizationStrategy` | `src/core/strategies/__init__.py` | ABC: `evaluate(kpis) → PolicyDecision` |
| `ThresholdBasedStrategy` | `src/core/strategies/__init__.py` | PRB-utilization threshold rule |
| `MlBasedStrategy` | `src/core/strategies/__init__.py` | Wraps a callable model (placeholder) |
| `RAppPlatformFactory` | `src/factories/__init__.py` | ABC: creates `ScenarioRunner`, `TelemetryCollector`, `KpiAnalyzer` |
| `GnbTelemetryAdapter` | `src/rapp/adapters/vendor/__init__.py` | Normalises vendor metrics → `KpiReport` |

---

## HTTP Endpoints

| Path | Method | Response |
|---|---|---|
| `/` | GET | JSON health payload |
| `/health` | GET | JSON health payload (alias) |
| `/status` | GET | JSON health payload (alias) |
| `/stats` | GET | HTML page with auto-refresh every 5 s |

---

## Configuration

Runtime configuration is read exclusively from environment variables.
Precedence: `RAPP_*` prefix overrides legacy names.

| Env var | Legacy | Default | Description |
|---|---|---|---|
| `RAPP_HOST` | `HOST` | `0.0.0.0` | Bind address |
| `RAPP_PORT` | `PORT` | `8080` | Listen port |
| `RAPP_SERVICE_NAME` | `SERVICE_NAME` | `template-app` | Service identifier in health payload |

Copy `config/.env.example` to `.env` and fill in project-specific values.
Never commit `.env` to version control.

---

## Conventions

### Python style
- **Python 3.12** (runtime); uses `from __future__ import annotations` for deferred evaluation throughout.
- **Stdlib only** — `requirements.txt` is intentionally empty; add third-party deps only as needed.
- Docstrings follow **Sphinx / reStructuredText** style with `:param:` and `:return:` fields (required by BMW Lab SOP §4).
- All 3GPP metric parameters must include a hyperlink to the authoritative specification (SOP §8).
- Frozen `dataclass` for immutable value objects; `Protocol` for structural typing of ports.

### Git
- Branch: **`rapp`**
- Commit message format:
  ```
  <Short imperative summary title>

  Work Start: hh.mm

  Summary:
  <One-paragraph summary>

  Details:
  1. <Change 1>
  2. <Change 2>
  ```
- Do not include LLM co-author trailers.

### Container
- Base image: `python:3.12-slim`; `WORKDIR /src`.
- `COPY src/requirements.txt` then `pip install`, then `COPY ./src .`
- Default port: **8080**.

### Documentation
- `README.md` at repo root follows the [BMW Lab SOP project-documentation template](https://github.com/bmw-ece-ntust/SOP/blob/master/project-documentation.md).
- Every component should have: Installation Guide, User Guide, and links from the Project Documentation.

---

## Terminology

| Term | Meaning |
|---|---|
| **rApp** | Non-RT RIC application in the O-RAN architecture |
| **xApp** | Near-RT RIC application in the O-RAN architecture |
| **Non-RT RIC** | Non-Real-Time RAN Intelligent Controller (≥ 1 s control loop) |
| **Near-RT RIC** | Near-Real-Time RAN Intelligent Controller (10 ms – 1 s control loop) |
| **SMO** | Service Management and Orchestration (O-RAN layer hosting Non-RT RIC) |
| **gNB** | 5G base station (NR Node B) |
| **PRB** | Physical Resource Block — basic scheduling unit in NR |
| **DRB.PrbUtilDL/UL** | 3GPP TS 28.552 KPI for DL/UL PRB utilization ratio |
| **KpiReport** | Internal frozen dataclass aggregating 3GPP-standardized KPIs per cell |
| **PolicyDecision** | Enum output of an `OptimizationStrategy`: `ACTIVE`, `SLEEP`, or `HANDOVER` |
| **BMW Lab** | Broadband Mobile Wireless Lab, ECE Department, NTUST |
| **SOP** | Lab Standard Operating Procedure (source: [bmw-ece-ntust/SOP](https://github.com/bmw-ece-ntust/SOP)) |
| **nonrtric-rapp-healthcheck** | Reference rApp from O-RAN SC that defines the canonical Python project layout |

---

## External Links

| Resource | URL |
|---|---|
| O-RAN SC nonrtric-rapp-healthcheck | https://gerrit.o-ran-sc.org/r/admin/repos/nonrtric/plt/rappmanager |
| BMW Lab SOP | https://github.com/bmw-ece-ntust/SOP |
| SOP project-documentation template | https://github.com/bmw-ece-ntust/SOP/blob/master/project-documentation.md |
| SOP source-code-guide | https://github.com/bmw-ece-ntust/SOP/blob/master/source-code-guide.md |
| 3GPP TS 28.552 (KPI definitions) | https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/ |
| Refactoring Guru — Adapter | https://refactoring.guru/design-patterns/adapter |
| Refactoring Guru — Abstract Factory | https://refactoring.guru/design-patterns/abstract-factory |
| Refactoring Guru — Strategy | https://refactoring.guru/design-patterns/strategy |
| Helm v3 | https://helm.sh |
| O-RAN Alliance | https://www.o-ran.org |
