# TODO.md — Task List

> Format: `[ ]` not started · `[~]` in progress · `[x]` done
> Sections: **Now** (this session) · **Next** (next 1–2 sessions) · **Later** (backlog)

---

## Now

_Nothing pending._

## Next

- [ ] Run `/graphify .` once the template is adapted for a real project, and commit the resulting `graphify-out/`
- [ ] Implement `E2Client` for O-RAN SC RMR transport (`xapp-frame-py` integration)
- [ ] Implement `E2Client` for FlexRIC gRPC transport
- [ ] Wire VES push-receiver endpoint to HTTP server (FastAPI route → `VesEventAdapter.dispatch()`)
- [ ] Implement `IntentResolutionService.resolve()` for energy-saving use case
- [ ] Implement `NimAdapter` under `src/rapp/adapters/nim/` (NVIDIA NIM REST client)
- [ ] Add rApp lifecycle state machine (onboard → prime → instantiate → running) per O-RAN WG2
- [ ] Add `RAPP_PLATFORM=osc` integration test against VIAVI TA rApp endpoints
- [ ] Migrate HTTP server from stdlib `BaseHTTPRequestHandler` to FastAPI + uvicorn
- [ ] Add pytest suite under `tests/` covering `MockPlatformFactory` + `IntentResolutionService`
- [ ] Generate Sphinx API docs and link from `CONTEXT.md`
- [ ] Add `docs/INSTALLATION-GUIDE.md`

## Later

- [ ] Add CSAR/TOSCA packaging for O-RAN SC rApp Manager onboarding
- [ ] Add `ConfigManager` pattern (JSON + env var override) alongside `Settings` dataclass
- [ ] Add ns-3 E2 simulation connector (`Ns3ScenarioRunner` using ns-O-RAN integration)
- [ ] Evaluate A1 policy-driven strategy (`A1PolicyStrategy` receiving policy → selecting `OptimizationStrategy`)
- [ ] Add multi-Near-RT-RIC A1 policy distribution (iterate `NetworkTopology.cells()`)
- [ ] Add O1 YANG change-notification subscription (not just get/set config)
