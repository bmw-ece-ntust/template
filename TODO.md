# TODO.md — Task List

> Format: `[ ]` not started · `[~]` in progress · `[x]` done
> Sections: **Now** (this session) · **Next** (next 1–2 sessions) · **Later** (backlog)

---

## Now

_Nothing pending._

## Next

- [ ] Add a worked `EnergySavingStrategy` and register it in `_STRATEGIES` (WG1 use case)
- [ ] Generalize A1: an Energy-Saving policy type instead of reusing `ORAN_TrafficSteering_0.1.0`
- [ ] Implement `IntentResolutionService.resolve()` for the energy-saving use case
- [ ] Implement `E2Client` for O-RAN SC RMR transport (`ricxappframe` / xapp-frame-py)
- [ ] Implement `E2Client` for FlexRIC gRPC transport
- [ ] Wire VES push-receiver endpoint to the HTTP server (`VesEventAdapter.dispatch()`)
- [ ] Implement `NimAdapter` at `src/handlers/nim.py` (NVIDIA NIM REST client) for `NvidiaModelStrategy`
- [ ] Add an `xapp-descriptor/config.json` (RMR tx/rx) for the xApp onboarding profile
- [ ] Add rApp lifecycle state machine (onboard → prime → instantiate → running) per O-RAN WG2
- [ ] Add `RAPP_PLATFORM=osc` integration test against VIAVI TA rApp endpoints
- [ ] Migrate HTTP server from stdlib `BaseHTTPRequestHandler` to FastAPI + uvicorn
- [ ] Publish Sphinx HTML (ReadTheDocs or GitHub Pages) from CI
- [ ] Add `docs/INSTALLATION-GUIDE.md`

## Later

- [ ] Add a hysteresis `ThresholdBasedStrategy` variant (uses cell on/off state to avoid flapping)
- [ ] Add a third vendor adapter (e.g. `handlers/adapters/aruba/` for WiFi APs)
- [ ] Add CSAR/TOSCA packaging for O-RAN SC rApp Manager onboarding
- [ ] Add `ConfigManager` pattern (JSON + env override) alongside `Settings`
- [ ] Add ns-3 E2 connector (`Ns3ScenarioRunner` via ns-O-RAN) if needed
- [ ] Evaluate A1 policy-driven strategy (`A1PolicyStrategy` selecting an `OptimizationStrategy`)
- [ ] Add multi-Near-RT-RIC A1 policy distribution (iterate `NetworkTopology.cells()`)
- [ ] Add O1 YANG change-notification subscription (not just get/set config)
- [ ] Feed `docs/sop-review.md` suggestions back into the BMW Lab SOP repo
