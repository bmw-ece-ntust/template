# TODO.md — Task List

> Format: `[ ]` not started · `[~]` in progress · `[x]` done
> Sections: **Now** (this session) · **Next** (next 1–2 sessions) · **Later** (backlog)

---

## Now

- [x] Rebuild the vendor axis: `factories/ns3` `viavi` `oai` `ocudu` (each =
      `<Vendor>Param` enum + `VendorParameterMap` + `KpiAnalyzer` Adapter +
      factory subclassing `OscPlatformFactory`); removed `mock` / `physical` /
      `ericsson` / `nokia`
- [x] `_FACTORY_BY_PLATFORM` table in `main.py` (adding a vendor = one row,
      no new `if` branch); default platform now `osc`
- [x] PEE energy counters (`PEE.AvgPower` §5.1.1.19.2.1, `PEE.Energy`
      §5.1.1.19.3) in `ThreeGPPKpi` + `KpiReport.avg_power_w` / `energy_kwh`
- [x] Test double `FakeTelemetryCollector` moved to `tests/conftest.py`;
      vendor adapter tests rewritten for the four vendors
- [x] Examples: `vendor_viavi_adapter` (Adapter + PEE + unmapped-key demo);
      `threshold_energy_saving_rapp` now uses `EnergySavingStrategy` + OSC analyzer
- [x] One-class-per-file rule mirrored into `CLAUDE.md` (SOP programming.md
      Section 5.1 already defines it; verified)
- [ ] Validate the four vendor parameter maps against deployed releases
      (ns-O-RAN KPM report, VIAVI RIC Test KPI list, OAI/FlexRIC KPM, OCUDU
      metrics reference) — maps are illustrative until then

## Next

- [x] Add a worked `EnergySavingStrategy` and register it in `_STRATEGIES` (WG1 use case)
- [ ] Generalize A1: an Energy-Saving policy type instead of reusing `ORAN_TrafficSteering_0.1.0`
- [ ] Implement `IntentResolutionService.resolve()` for the energy-saving use case
- [ ] Implement `E2Client` for O-RAN SC RMR transport (`ricxappframe` / xapp-frame-py)
- [ ] Implement `E2Client` for FlexRIC gRPC transport
- [ ] Wire VES push-receiver endpoint to the HTTP server (`VesEventAdapter.dispatch()`)
- [ ] Implement a NVIDIA NIM REST client (injected as the `nim_infer` callable) for `NvidiaModelStrategy` — not under `handlers/` (O-RAN-only)
- [ ] Add an `xapp-descriptor/config.json` (RMR tx/rx) for the xApp onboarding profile
- [ ] Implement the rApp lifecycle state machine in code (onboard → prime → instantiate → running) per O-RAN WG2 — diagrams added to CONTEXT.md 2026/07/07
- [ ] Add `RAPP_PLATFORM=osc` integration test against VIAVI TA rApp endpoints
- [ ] Migrate HTTP server from stdlib `BaseHTTPRequestHandler` to FastAPI + uvicorn
- [ ] Publish Sphinx HTML (ReadTheDocs or GitHub Pages) from CI
- [ ] Add `docs/INSTALLATION-GUIDE.md`

## Later

- [ ] Add a hysteresis `ThresholdBasedStrategy` variant (uses cell on/off state to avoid flapping)
- [ ] Add a WiFi vendor factory (`factories/aruba/`, `NodeType.WIFI_AP`)
- [ ] Add CSAR/TOSCA packaging for O-RAN SC rApp Manager onboarding
- [ ] Add `ConfigManager` pattern (JSON + env override) alongside `Settings`
- [ ] Add ns-3 E2 connector (`Ns3ScenarioRunner` via ns-O-RAN) if needed
- [ ] Evaluate A1 policy-driven strategy (`A1PolicyStrategy` selecting an `OptimizationStrategy`)
- [ ] Add multi-Near-RT-RIC A1 policy distribution (iterate `NetworkTopology.cells()`)
- [ ] Add O1 YANG change-notification subscription (not just get/set config)
- [ ] Feed `docs/sop-review.md` suggestions back into the BMW Lab SOP repo
