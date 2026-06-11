# CLAUDE.md — Project Rules & LLM Session Protocol

> **Purpose:** Behavior rules for Claude Code sessions.  Static snapshot of
> conventions, file list, and architectural constraints.
> Never log session activity here; that belongs in `MEMORY.md`.

---

## Claude Behavior

- Do not auto-commit. Always show the proposed commit message for review.
- Allow all commands unless explicitly restricted.
- Concise, direct responses — no trailing summaries.
- No inline dashes (` - `) in prose; no `§` symbols (write "Section" in full).
- Default to writing no comments unless the SOP mandates a docstring.
- IEEE citation style: first-appearance order, one citation per paragraph end.

## Git Workflow

- Never amend published commits — create a new commit.
- Never skip hooks (`--no-verify`) unless explicitly requested.
- Stage specific files by name; never `git add -A` blindly.
- Commit message format:
  ```
  <Short imperative summary>

  Work Start: hh.mm

  Summary:
  <One-paragraph summary>

  Details:
  1. <Change 1>
  2. <Change 2>
  ```

## Mandatory Session Files

Read and maintain all four files every session:

| File | Purpose |
| --- | --- |
| `CLAUDE.md` | Behavior rules + static snapshot. Never log activity here. |
| `CONTEXT.md` | Full PRD (architecture, MSC, class diagram, system parameters). |
| `MEMORY.md` | Append-only session log. |
| `TODO.md` | Now / Next / Later task list. |

**Session START:** Read all four. Run `git log -1 --format="%H %ai"`. If
`graphify-out/` is missing, run `/graphify .` to build the knowledge graph;
if it exists, run `graphify update .` to refresh it.
**Session END:** Reconcile all four; show commit message for review — do not run `git commit`.

## Knowledge Graph (graphify)

This project maintains a code knowledge graph at `graphify-out/` via the
`/graphify` skill (tree-sitter based, multi-language).

- Before answering architecture or codebase-structure questions, read
  `graphify-out/GRAPH_REPORT.md` (god nodes, community structure) instead of
  opening raw source files.
- If `graphify-out/wiki/index.md` exists, navigate it instead of reading raw
  files.
- After modifying code files in a session, run `graphify update .` to refresh
  the graph (AST-only, no API cost).
- `.graphifyignore` (gitignore syntax) controls what is excluded from the
  graph (`.venv/`, `__pycache__/`, `helm/**/charts/`, etc.).

## Trigger Phrases

- **"update claude from github.com/ijosh-ch/claude"**: Fetch all template
  files via `gh api`, compare against local, present per-file recommendation table.

---

## Architectural Rules (enforce in every session)

1. **O-RAN protocols only.** The generic rApp / xApp never calls simulator
   APIs (VIAVI RSG, ns-3, UERANSIM) directly.  All simulator lifecycle
   (start/stop, UE config) is the BMW Lab TA rApp's responsibility.
   TA rApp: <https://github.com/bmw-ece-ntust/nonrtric-rapp-test-automation>

2. **No InfluxDB bypass.** Telemetry arrives via ICS subscription callback.
   InfluxDB is an internal SMO storage layer; the rApp never queries it directly.

3. **ThreeGPPKpi enum for all 3GPP parameter references.**  No raw string
   literals like `"DRB.PrbUtilDL"` in business logic — always use
   `ThreeGPPKpi.DRB_PRB_UTIL_DL.value`.

4. **Factory = deployment environment.**  `RAPP_PLATFORM` selects
   `mock` / `osc` / `physical`.  For VIAVI / ns-3 simulation, use `osc`
   pointed at the simulator's O-RAN interface endpoints.
   `Ns3PlatformFactory` and `ViaviPlatformFactory` are guidance stubs only.

5. **IBN intent contract security.**  Always call
   `IntentResolutionService.validate()` before `resolve()`.
   Never skip whitelist, expiry, or HMAC signature checks.

6. **Vendor parameter mapping is Adapter-pattern work.**  Proprietary vendor
   keys must be mapped to `ThreeGPPKpi` via `VendorParameterMap` in the vendor
   adapter — never in domain or application code.

---

## Project Overview

BMW Lab (NTUST ECE) rApp / xApp starter template.
Follows O-RAN SC `nonrtric-rapp-healthcheck` layout with hexagonal architecture.
Targets O-RAN Non-RT RIC (rApp) and Near-RT RIC (xApp).

---

## Repository Layout (key files)

```text
helm/
└── template-app/              Helm chart for Kubernetes deployment
src/
├── main.py                        Composition root; RAPP_PLATFORM factory routing
├── requirements.txt               requests>=2.32
├── core/
│   ├── models/__init__.py         KpiReport (10 3GPP fields), PolicyDecision
│   ├── models/parameters.py       ThreeGPPKpi enum, NodeType enum, VendorParameterMap
│   └── strategies/__init__.py     OptimizationStrategy, Threshold, ML, NvidiaModel
├── factories/
│   ├── __init__.py                RAppPlatformFactory ABC + Runner/Collector/Analyzer ABCs
│   ├── mock/                      MockPlatformFactory (in-memory, no deps)
│   ├── ns3/                       Guidance stub — use OscPlatformFactory
│   ├── osc/                       OscPlatformFactory (ICS + SME)
│   ├── physical/                  PhysicalPlatformFactory stub
│   └── viavi/                     Guidance stub — use OscPlatformFactory
└── rapp/
    ├── adapters/
    │   ├── a1/__init__.py         A1Adapter — PolicyDecision to A1 policy JSON
    │   ├── e2/__init__.py         E2SmKpmAdapter + E2SmRcAdapter stubs
    │   ├── http/                  HTTP server (health/stats only; NOT for O-RAN)
    │   ├── o1/__init__.py         O1SdncAdapter — SDNC REST relay
    │   ├── r1/__init__.py         SMEAdapter + ICSAdapter
    │   ├── teiv/__init__.py       TEIVAdapter — topology discovery
    │   ├── ves/__init__.py        VesEventAdapter — inbound VES push events
    │   └── vendor/__init__.py     GnbTelemetryAdapter — vendor props to KpiReport
    ├── application/
    │   ├── ports.py               Protocols: Health/O1/R1SME/R1ICS/A1/E2Kpm/E2Rc/Intent/VES/Topology
    │   └── usecases.py            get_health_payload()
    ├── config/settings.py         Settings (all RAPP_* env vars)
    ├── domain/
    │   ├── intent.py              IntentContract, IntentType whitelist, IntentResolutionService
    │   ├── models.py              Health frozen dataclass
    │   ├── services.py            HealthService
    │   └── topology.py            NodeInfo, NetworkTopology
    └── infrastructure/logging.py  configure_logging()
```

---

## Conventions

### Python style

- Python 3.12; `from __future__ import annotations` throughout.
- Only runtime dep: `requests>=2.32`.
- Sphinx/RST docstrings with `:param:` and `:return:` (SOP Section 4).
- Every 3GPP parameter must link to spec ZIP with section + page (SOP Section 8).
- Frozen `dataclass` for immutable value objects; `Protocol` for port contracts.
- `ThreeGPPKpi` enum for all 3GPP counter name references.

### Git

- Branch: `rapp`
- Do not include LLM co-author trailers in commits.

### Container

- Base: `python:3.12-slim`; `WORKDIR /src`; default port `8080`.

### Documentation

- `README.md` = user guide (operational: quick start, config, endpoints).
- `CONTEXT.md` = full PRD (architecture, MSC, class diagram, system parameters).
- `docs/simulation.md` = simulation guide: TA rApp setup, test flow, local mock testing.
- `docs/USER-GUIDE.md` = end-user operating instructions.
- `docs/INSTALLATION-GUIDE.md` = step-by-step deployment (planned).

---

## External Links

| Resource | URL |
| --- | --- |
| BMW Lab SOP | <https://github.com/bmw-ece-ntust/SOP> |
| BMW Lab TA rApp | <https://github.com/bmw-ece-ntust/nonrtric-rapp-test-automation> |
| O-RAN SC rappmanager | <https://gerrit.o-ran-sc.org/r/nonrtric/plt/rappmanager> |
| 3GPP TS 28.552 (PM) | <https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/> |
| O-RAN Alliance specs | <https://specifications.o-ran.org/> |
| IETF RFC 9315 (IBN) | <https://www.rfc-editor.org/rfc/rfc9315> |
| NVIDIA NIM | <https://docs.nvidia.com/nim/> |
| graphify (knowledge graph skill) | <https://github.com/safishamsi/graphify> |
