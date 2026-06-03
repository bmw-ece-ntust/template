# MEMORY.md — Session Log

> **Rules:** Append only — never edit past entries.
> Each entry: `### yyyy/mm/dd` header, concise bullet decisions.

---

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
