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
| `CONTEXT.md` | Full PRD (architecture, MSC, class diagram, state machine, system parameters). |
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

4. **Every swappable axis is config-selected the same way.**  `RAPP_PLATFORM`
   selects the deployment factory (`mock` / `osc` / `physical` / `ericsson` /
   `nokia`) in `main._build_factory`; `RAPP_STRATEGY` selects the algorithm via
   `controllers.strategies.make_strategy`.  Vendor support is a platform: each
   vendor is its own Abstract Factory (`factories/<vendor>/`), not a separate
   axis.  Never hard-code these in the composition root.  For VIAVI / ns-3
   simulation, use `osc` pointed at the simulator's O-RAN interface endpoints
   (`Ns3`/`Viavi` factories are stubs).

5. **IBN intent contract security.**  Always call
   `IntentResolutionService.validate()` before `resolve()`.
   Never skip whitelist, expiry, or HMAC signature checks.

6. **Vendor parameter mapping is Adapter-pattern work.**  Proprietary vendor
   keys must be mapped to `ThreeGPPKpi` via `VendorParameterMap` inside the
   vendor platform factory (`factories/<vendor>/`, in its `KpiAnalyzer`) —
   never in models, controllers, or the `handlers/interfaces/` O-RAN adapters.

---

## Project Overview

BMW Lab (NTUST ECE) rApp / xApp starter template.
Simple, professional **MVC + handlers** architecture (models / controllers /
views, with O-RAN I/O in handlers — the shape of OSC `ric-app-kpimon-go`).
Targets O-RAN Non-RT RIC (rApp) and Near-RT RIC (xApp).

---

## Repository Layout (key files)

> **Authoritative source:** the code is the source of truth. Structure is
> MVC + handlers (inspired by OSC `ric-app-kpimon-go`): O-RAN standard interface
> adapters live in `src/handlers/interfaces/*.py`; proprietary vendor handling is
> a deployment concern owned by per-vendor Abstract Factories in
> `src/factories/<vendor>/`. `handlers/` is O-RAN-standard only. No `rapp/`
> wrapper, no `application/` layer.

```text
pyproject.toml                     Project metadata + ruff/mypy/pytest config
requirements-dev.txt               Dev/docs tooling (-e .[dev,docs]); runtime deps in src/requirements.txt
helm/template-app/                 Helm chart for Kubernetes deployment
tests/                             pytest suite (models, controllers, adapters)
examples/                          Runnable end-to-end usage scripts
src/
├── main.py                        Composition root; RAPP_PLATFORM factory routing + control cycle
├── requirements.txt               requests>=2.32
├── models/                        M — data only, no I/O
│   ├── kpi.py                     KpiReport (11 3GPP fields), PolicyDecision, from_3gpp
│   ├── parameters.py              ThreeGPPKpi enum, NodeType enum, VendorParameterMap
│   ├── topology.py                NodeInfo, NetworkTopology
│   ├── intent.py                  IntentContract, IntentType whitelist, IntentResolutionService
│   └── health.py                  Health frozen dataclass
├── controllers/                   C — orchestration + algorithms
│   ├── kpi_controller.py          KpiController (Context): collect → analyze → decide; set_strategy
│   ├── health.py                  HealthService + get_health_payload
│   └── strategies.py              OptimizationStrategy, Threshold/ML/Nvidia, make_strategy selector
├── handlers/                      O-RAN STANDARD interfaces only (Adapter pattern)
│   └── interfaces/                a1.py e2.py o1.py r1.py teiv.py ves.py
├── factories/                     Abstract Factory: deployment + vendor selector (RAPP_PLATFORM)
│   ├── mock/ osc/ physical/       standard environments (osc = 3GPP names, no vendor xlat)
│   ├── ns3/ viavi/                simulation guidance stubs (use osc)
│   ├── ericsson/                  EricssonParam enum + map + analyzer(Adapter) + factory
│   └── nokia/                     NokiaParam enum + map + analyzer(Adapter) + factory
├── views/                         V — health/stats HTTP + Grafana dashboards
│   ├── http/                      api.py, server.py (health/stats only; NOT for O-RAN)
│   └── grafana/                   rapp-kpi-dashboard.json + README (SMO Grafana)
└── config/                        settings.py (RAPP_* env vars) + logging.py
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

- `README.md` = Getting Started + user guide (quick start, config, deploy, endpoints).
- `CONTEXT.md` = full PRD (architecture, MSC, class diagram, state machine, system parameters).
- `docs/PRD-TEMPLATE.md` = fill-in PRD for a new rApp (design contract).
- `docs/llm-authoring-guide.md` = PRD → rApp generation workflow for LLMs.
- `docs/osc-reference-study.md` = OSC reference-app structure survey.
- `docs/sop-review.md` = assessment + improvement suggestions for the BMW Lab SOP.
- `docs/simulation.md` = simulation guide: TA rApp setup, test flow, local mock testing.
- `docs/USER-GUIDE.md` = end-user operating instructions.
- `docs/INSTALLATION-GUIDE.md` = step-by-step deployment (planned).
- API reference = Sphinx (`docs/conf.py`); build to `docs/_build/html`.

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
