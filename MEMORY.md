# MEMORY.md — Session Log

> **Rules:** Append only — never edit past entries.
> Each entry: `### yyyy/mm/dd` header, concise bullet decisions.

---

### 2026/06/24 (session 9) — Single-axis refactor: handlers/interfaces + per-vendor factories

**Duration**: 2026/06/24: 09.12 – 09.58

- **Goal restated by user:** a well-structured OSC rApp implementing OOP + MVC +
  multi-vendor, with the factory following refactoring.guru Abstract Factory.
- **Removed duplication:** deleted orphaned `src/core/` and `src/rapp/` (stale
  `__pycache__` only, no live source) — the real source lives under `src/`.
- **Resolved the axis question:** vendor and platform are NOT orthogonal. On the
  `osc` path ICS delivers telemetry already in 3GPP names (no vendor translation);
  proprietary names only appear when reading a vendor management plane directly.
  So vendor is a *sub-case of platform*. Reversed the earlier "two orthogonal
  axes" decision (session 8) → **one axis** `RAPP_PLATFORM = mock | osc | physical
  | ericsson | nokia`.
- **`handlers/` is O-RAN-standard only:** `git mv` the six interface adapters into
  `handlers/interfaces/` (a1 e2 o1 r1 teiv ves). Deleted `handlers/adapters/` +
  `handlers/vendor.py` (removed `VendorAdapter` ABC + registry `get_vendor_adapter`,
  `VendorTelemetryClient`, dead `GnbTelemetryAdapter`).
- **Each vendor is its own concrete Abstract Factory:** `factories/ericsson/` and
  `factories/nokia/` each carry their proprietary `*Param` enum + `*_PARAM_MAP`
  (`VendorParameterMap`) + `ScenarioRunner`/`TelemetryCollector`/`KpiAnalyzer`/
  `PlatformFactory`. The Adapter (proprietary → `ThreeGPPKpi`) lives inside the
  analyzer; `VendorParameterMap` stays in `models/parameters.py` (pure data).
- Wired `ericsson`/`nokia` into `main._build_factory` + `--platform` choices; added
  `RAPP_EMS_BASE_URL` (`Settings.ems_base_url`). Rewrote `tests/test_vendor_adapters.py`
  (analyzers + `_build_factory` resolution, no network) and the Ericsson example.
- Updated all docs to the new layout: `CLAUDE.md` (Rules 4 & 6, layout tree,
  authoritative note), `CONTEXT.md` (layer table, interface table, class index,
  changelog), `README.md` (capabilities, env vars, platforms, prune table, tree),
  `docs/llm-authoring-guide.md`, `docs/PRD-TEMPLATE.md`, `docs/sop-review.md`,
  `docs/osc-reference-study.md`, `TODO.md`.
- Verified (pytest/graphify unavailable in env): 19/19 import smoke OK, examples
  run, 14/14 touched tests pass via a minimal shim.

### 2026/06/15 (session 8) — Strategy selection + ES guardrails

**Duration**: 2026/06/15: 15.08 – 19.17

- **"Will this template mislead an LLM building an Energy Saving rApp from O-RAN
  WG1?"** Analysis: bones are right (`IntentType.ENERGY_SAVING`,
  `ThresholdBasedStrategy` is the ES algorithm, R1-in/A1-out shape) but four
  traps: the A1 example is Traffic-Steering-specific (`ORAN_TrafficSteering_0.1.0`
  plus PREFER/AVOID/FORBID), `PolicyDecision` conflates TS+ES+HO, E2 handlers invite
  wrong rApp wiring, and "WG1" is a use-case spec not an interface.
- Per user decision (analysis only, no ES example/A1 generalization): added a
  **copy-and-rename** "Author a new rApp" section to README with a prune table
  (rApp vs xApp / single vendor / one algorithm) and guardrail callouts (rApp
  emits A1/O1 not E2; WG1 = use-case provenance; don't reuse the TS A1 schema for
  Energy Saving). The repo is a template, not an edit-in-place app.
- **Clarified pattern boundaries** (in Q&A, now reflected in docs): `factories/`
  = Abstract Factory keyed on *deployment environment* (does NOT do vendor
  translation — ICS already delivers 3GPP names); `handlers/adapters/<vendor>/`
  = Adapter for *proprietary* params. Orthogonal axes.
- **Fixed the Strategy pattern per refactoring.guru** (the "best fit", kept
  essential): `controllers/strategies.py` gained a plain `_STRATEGIES` registry +
  `make_strategy(name, **params)` selector (same idiom as `get_vendor_adapter`);
  `KpiController` is now a true Context with `set_strategy()` for runtime swap;
  `main.py` uses `make_strategy(settings.strategy)` with a `RAPP_STRATEGY` env var
  plus a `--strategy` flag. ML/NIM strategies stay out of the by-name registry (they
  need an injected callable). Unknown strategy fails fast at startup.
- Gotcha fixed: `ThresholdBasedStrategy.threshold_high` was stored but never read
  (dead param) — removed, with a note that two thresholds only make sense for
  hysteresis (needs cell state). Also fixed the stale
  `src/rapp/handler/interfaces/nim.py` docstring path → `src/handlers/nim.py`.
- Added `requirements-dev.txt` (`-e .[dev,docs]`, single-sources pyproject
  extras) to close the runtime-vs-dev dependency question.
- Decision: no heavyweight `StrategyFactory` ABC — strategy selection does not
  vary by platform, so a plain registry/selector is the essential form. Now all
  three swappable axes (`RAPP_PLATFORM`, `RAPP_STRATEGY`, vendor) are selected
  identically. Full gate green: 41 tests, 98% coverage, ruff/mypy/sphinx/helm.

### 2026/06/15 (session 7) — MVC restructure

**Duration**: 2026/06/15: 15.08 – (cont.)

- User review of the layout: questioned the `rapp/` wrapper, the `application/`
  layer (Hexagonal use-cases/ports, not a GoF pattern, absent from OSC), and
  asked for MVC (models/controllers/views) with O-RAN I/O in `handlers/`.
- Re-analysed `ric-app-kpimon-go` (called "the best xApp") from its graphify
  output: the real app is just `kpimon.go` (entry) + `control/` (control.go =
  controller, e2ap/e2sm/f1ap = protocol handlers, types.go = models). No
  `application` layer, no wrapper package. Validated the user's instinct.
- Restructured `src/` from hexagonal `rapp/{domain,application,handler,...}` +
  `core/` + `factories/` to flat **MVC + handlers**:
  `models/` (kpi, parameters, topology, intent, health),
  `controllers/` (kpi_controller, health, strategies),
  `handlers/` (a1 e2 o1 r1 teiv ves vendor + `adapters/<vendor>`),
  `views/` (http + grafana), `factories/`, `config/` (settings + logging).
- Dropped `application/ports.py` (Protocols were docstring-only except
  `HealthPort`) and `application/usecases.py` (folded `get_health_payload` into
  `controllers/health.py`). Added `controllers/kpi_controller.py` (`KpiController`
  collect→analyze→decide), wired into `main.py` so the startup logs a real
  control cycle.
- Added `KpiReport.from_3gpp` stays in `models/kpi.py`; `models/__init__`
  re-exports the common value objects (`from models import KpiReport`).
- Added the Grafana view: `views/grafana/rapp-kpi-dashboard.json` (PRB, UEs,
  decision timeline) + README explaining the SMO Grafana/InfluxDB wiring
  (visualization is config, not Python — same as kpimon writing metrics to a DB).
- Rewrote every import (perl pass over src/tests/examples), updated pyproject
  coverage source, Sphinx `reference.rst`, and all layout docs (CLAUDE.md,
  CONTEXT.md, README.md, src/README.md, llm-authoring-guide, PRD-TEMPLATE,
  osc-reference-study, sop-review). Full gate green again.

### 2026/06/15 (session 6)

**Duration**: 2026/06/15: 13.15 – 15.08

- Studied 10 OSC reference apps (cloned to `~/Documents/GitHub/OSC/`, graphified
  AST-only/free): healthcheck, orufhrecovery, ransliceassurance, rappmanager,
  rappcatalogue (rApps) + hw-python, ad, qp, kpimon-go, rc (xApps). Findings in
  `docs/osc-reference-study.md`: OSC apps are flat/procedural or Handler+Manager
  (hw-python) on `ricxappframe`+RMR; none use hexagonal layers, the 3 SOP
  patterns together, or a 3GPP enum, but all ship tests/Sphinx/CI/descriptor —
  scaffolding this template historically lacked.
- Generated the template knowledge graph (`graphify-out/`): `ThreeGPPKpi` is the
  top god node (35 edges), confirming the enum-centric design.
- Fixed doc/code drift: CLAUDE.md + CONTEXT.md described `src/rapp/adapters/`
  but code is `src/rapp/handler/interfaces/*.py`. Realigned both. Removed the
  empty `simulation/` placeholder (testing delegated to TA rApp; recorded as an
  intentional SOP deviation in `docs/sop-review.md`).
- Added multi-vendor proprietary adapters under `src/rapp/handler/adapters/`:
  `VendorAdapter` ABC + auto-registry (`get_vendor_adapter`), `ericsson/` and
  `nokia/` each with a proprietary `str` enum + `VendorParameterMap` →
  `ThreeGPPKpi`. Added `KpiReport.from_3gpp()` as the shared standardized-dict →
  report bridge and `VendorParameterMap.keys()`.
- Industrial tooling: `pyproject.toml` (ruff + mypy + pytest + coverage, src
  layout), recreated `tests/` (36 tests, 98% coverage on core+domain, 80% gate),
  `.pre-commit-config.yaml`, `.github/workflows/ci.yml` (lint→type→test→docs→helm).
  Fixed all ruff (kept `class X(str, Enum)`, ignored UP042) and mypy issues.
- Sphinx API docs (`docs/conf.py`, `index.rst`, `reference.rst`, `Makefile`);
  builds clean with `-W` after fixing two RST docstrings (settings table, mock
  example block).
- Hardened Helm chart: `configmap.yaml`, `secret.yaml`, `serviceaccount.yaml`,
  `ingress.yaml`, image helper, securityContext, resource requests/limits, tmp
  emptyDir for readOnlyRootFilesystem. Validated with `helm lint` + `helm
  template` (default + osc + ingress).
- LLM authoring kit: `docs/PRD-TEMPLATE.md`, `docs/llm-authoring-guide.md`, and
  `examples/` (threshold rApp, ericsson adapter, intent resolution) — all run
  network-free.
- SOP review (`docs/sop-review.md`): keep design-first + spec-traceability +
  production-readiness; ADD quality gates/CI/pre-commit/pyproject/enum
  rule/vendor-folder spec/IBN section; allow hexagonal layout; relax mandatory
  `simulation/` + `ns3`/`viavi` factory folders.

### 2026/06/11 (session 5)

- Resolved a stale `git stash pop` merge conflict in `README.md`: kept the
  project-specific rApp/xApp README (Quick Start, Config table, HTTP
  Endpoints, Deployment Platforms, Known Issues, Directory Layout, Links) and
  discarded a generic Node.js "Installation Guideline" placeholder template
  that had been stashed and didn't apply to this Python/O-RAN codebase.
- Integrated the `graphify` knowledge-graph skill (PyPI `graphifyy`,
  <https://github.com/safishamsi/graphify>) to reduce token consumption when
  Claude explores this codebase: installed `uv` (`~/.local/bin`) and
  `graphifyy` globally via `uv tool install`, then ran `graphify install` to
  register the `/graphify` skill for Claude Code (writes to
  `~/.claude/skills/graphify/`).
- Added `.graphifyignore` (gitignore syntax) excluding `.venv/`,
  `__pycache__/`, `*.py[cod]`, `graphify-out/`, `docs/drawio/`,
  `docs/upstream/`, `helm/**/charts/`, `dist/`, `build/`.
- Added a `## Knowledge Graph (graphify)` section to `CLAUDE.md` plus a
  Session START step: build `graphify-out/` with `/graphify .` if missing,
  else refresh with `graphify update .` (AST-only, no API cost).
- Cross-linked `graphify-out/GRAPH_REPORT.md` from `CONTEXT.md` Introduction
  and added an Execution Status row.
- Added a "Vibe-Coding with Claude Code" section to `README.md` documenting
  `/graphify .`, `graphify update .`, `graphify query/path/explain` usage.
- Added `graphify-out/` to `.dockerignore` (dev/doc artifact, not needed in
  the runtime image).
- Decision: did not generate `graphify-out/` yet — full extraction (`graphify
  extract .`) wants an LLM API key for the 16 doc/markdown files (code-only
  extraction of the 36 source files is free but was deferred). Tracked in
  `TODO.md` under Next: run `/graphify .` and commit `graphify-out/` once the
  template is adapted for a real project.

### 2026/06/03 (session 4)

- Removed `test/` directory entirely — simulation lifecycle is the BMW Lab TA rApp's responsibility; the generic rApp never calls simulator APIs.
- Moved Helm chart from `test/usecases/healthcheck/scriptversion/helm/template-app/` → `helm/template-app/` — deployment artifact belongs at repo root level, not under a test path.
- Created `docs/simulation.md` — canonical guide for simulation testing with the TA rApp: architecture diagram, setup steps, test spec upload, Phase 1/2 flow, local mock testing path, ns-3 options.
- Updated `config/.env.example` — all `RAPP_*` env vars documented with purpose and renewal notes; added `NVIDIA_API_KEY` stub.
- Decision: `docs/` is the canonical location for operational guides (`simulation.md`, `continerized.md`, `USER-GUIDE.md`). `helm/` is at repo root for deployment artifacts.

### 2026/06/03 (session 2)

- Implemented O1, R1/SME, R1/ICS, A1 interface adapters in `src/rapp/adapters/` following OSC's integration approach (requests-based REST) but with BMW Lab's code discipline (ABC + Protocol, Sphinx docs, hexagonal layers).
- Added `O1Client` ABC with class-attribute `_YANG_MAX_UES` override pattern — enables multi-vendor YANG key mapping without forking the adapter.
- Added `OscPlatformFactory` + `OscLifecycleRunner` / `OscIcsTelemetryCollector` / `OscKpiAnalyzer` in `src/factories/osc/`.
- Extended `ports.py` with `O1Port`, `R1SMEPort`, `R1ICSPort`, `A1Port` Protocols — application use-cases now have typed contracts for all O-RAN interfaces.
- Added `requests>=2.32` to `requirements.txt` — required by all O-RAN adapters; stdlib HTTP kept only for simulator trigger endpoints.
- Updated `CLAUDE.md` repository layout, architecture, and key-classes tables to reflect all new files.
- Architecture principle confirmed: Adapter bridges [vendor-proprietary YANG] ↔ [O-RAN standard ops] AND [O-RAN standard JSON] ↔ [BMW Lab KpiReport/PolicyDecision]. Two distinct directions, same pattern.

### 2026/06/03 (session 3)

- Added `ThreeGPPKpi` string enum + `NodeType` enum + `VendorParameterMap` in `src/core/models/parameters.py`.
- Expanded `KpiReport` with `gnb_id`, `node_type`, `dl_throughput_kbps`, `ul_throughput_kbps`, `rsrp_dbm`, `rsrq_db`, `sinr_db`; all fields default so existing callers compile unchanged.
- Created `src/rapp/domain/topology.py`: `NodeInfo` + `NetworkTopology` for multi-gNB / multi-vendor / WiFi AP cell registry.
- Created `src/rapp/domain/intent.py`: `IntentType` whitelist enum, `IntentContract` (HMAC-signed, frozen dataclass), `IntentResolutionService` with whitelist/expiry/signature checks — contract-based IBN following IETF RFC 9315.
- Created `src/rapp/adapters/e2/`: `E2Client` ABC, `E2SmKpmAdapter` (subscribe/indication→KpiReport), `E2SmRcAdapter` (apply_decision→E2ControlAck); transport-agnostic stubs for RMR or gRPC.
- Created `src/rapp/adapters/ves/`: `VesEventAdapter` parses inbound O1 VES event push (TS 28.532); dispatches to registered handlers.
- Created `src/rapp/adapters/teiv/`: `TEIVAdapter` queries TEIV REST API to populate `NetworkTopology`; includes `refresh_node()` for VES-driven updates.
- Expanded `ports.py` with `E2KpmPort`, `E2RcPort`, `IntentPort`, `VESPort`, `TopologyPort`.
- Updated vendor adapter to use `ThreeGPPKpi` enum values; added `NodeType` param + `gnb_id` to `get_kpi_report()`.
- Added `NvidiaModelStrategy` in strategies — delegates to `nim_infer` callable; NIM HTTP logic belongs in `src/rapp/adapters/nim/`.
- Updated `OscKpiAnalyzer.analyze()` to use `ThreeGPPKpi` enum + new KpiReport fields.
- Created `src/factories/mock/`: `MockPlatformFactory` with configurable KPI fixture; default `RAPP_PLATFORM`.
- Replaced `Ns3PlatformFactory` and `ViaviPlatformFactory` `NotImplementedError` stubs with guidance docstrings pointing to `OscPlatformFactory` + BMW Lab TA rApp.
- Updated `factories/__init__.py`: factories discriminate over deployment environments (mock/osc/physical), not simulator vendor.
- Updated `settings.py`: added `platform`, `sme_base_url`, `ics_base_url`, `callback_url`, `cell_id`, `intent_secret` fields from `RAPP_*` env vars.
- Updated `main.py`: `_build_factory()` routes `RAPP_PLATFORM` → `MockPlatformFactory` / `OscPlatformFactory` / `PhysicalPlatformFactory`.
- Rewrote `README.md` as concise user guide (quick start, config table, endpoints, platforms, known issues, directory layout).
- Rewrote `CONTEXT.md` as full PRD following SOP project-documentation.md structure (LLM-friendly, Mermaid diagrams, System Parameters table with Page/§).
- Updated `CLAUDE.md`: added O-RAN-only rule, InfluxDB bypass rule, ThreeGPPKpi enum rule, factory=environment rule, IBN contract security rule, vendor mapping rule.
- Updated `SOP/project-documentation.md`: added O-RAN Interface Compliance, Multi-vendor Parameter Mapping, Evaluation Metrics, Digital Twin Setup, Known Issues sections; changed README.md → CONTEXT.md as PRD.
- Updated `SOP/source-code-guide.md`: added O-RAN Protocol Rules (Section 7), 3GPP Parameter Enumeration (Section 8), Multi-vendor Support (Section 9), IBN Section (Section 10).

### 2025/05/30

- Installed Claude 4-file session system (CLAUDE.md behavior rules, CONTEXT.md, MEMORY.md, TODO.md) into the template repo.
- Created `.claude/settings.json` (bypassPermissions, additionalDirectories) and `.claude/prompts/` scripts.
- Gap analysis: OSC official xApps (ric-plt-xapp-frame-py) use framework inheritance + RMR message bus; OSC rApps (threshold-control-rapp) use flat class + SME/ICS (R1) + SDNC/NETCONF (O1). Neither uses the 3 BMW Lab SOP required design patterns.
- BMW Lab template has better architecture (hexagonal) and pattern discipline, but ZERO O1/R1/A1/E2 interface implementations.
- Decision: HTTP-only transport kept for simulator triggers only (ns-3, VIAVI). Real-platform factory should route through O1/R1/A1 adapters.
- Decision: Do NOT drop hexagonal architecture — it is strictly superior to OSC flat style for research extensibility.
- Identified gap: `src/factories/physical/` has no real NETCONF/SME clients; `src/rapp/adapters/` has no O1/R1/A1 adapters.
- Identified gap: stdlib-only constraint blocks `requests` (needed for R1/SME), `ncclient` (O1), `pydantic` (OpenAPI models).
- SOP improvements suggested: add O-RAN interface section, rApp lifecycle section, distinguish xApp vs rApp more clearly, add CSAR packaging notes.
