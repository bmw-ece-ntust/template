# OSC Reference Study — rApp / xApp Structure Survey

> **Purpose:** Ground this template's architecture in evidence. Ten O-RAN
> Software Community (OSC) reference apps were cloned into
> `~/Documents/GitHub/OSC/` and each was turned into a knowledge graph with
> graphify (AST only, no LLM cost) to study how production O-RAN apps are
> structured. This note records what they share, where they differ, and what
> this template should adopt or deliberately improve upon.

## Method

Each repo was shallow-cloned and analysed with structural (tree-sitter AST)
extraction, producing a per-repo `graphify-out/GRAPH_REPORT.md` and
`graph.json`. Graph size is a rough proxy for surface area and coupling.

| Repo | Role | Language | Nodes | Edges | Communities | Code files |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `nonrtric-rapp-healthcheck` | rApp | Python | 27 | 43 | 6 | 6 |
| `nonrtric-rapp-orufhrecovery` | rApp | Go | 202 | 328 | 31 | 49 |
| `nonrtric-rapp-ransliceassurance` | rApp | Go | 313 | 446 | 32 | 37 |
| `nonrtric-plt-rappmanager` | Platform (rApp lifecycle / CSAR) | Java | 1506 | 3191 | 131 | 264 |
| `nonrtric-plt-rappcatalogue` | Platform (rApp catalogue) | Python | 182 | 310 | 18 | 39 |
| `ric-app-hw-python` | xApp | Python | 97 | 147 | 17 | 22 |
| `ric-app-ad` | xApp | Python | 113 | 148 | 14 | 14 |
| `ric-app-qp` | xApp | Python | 88 | 112 | 11 | 13 |
| `ric-app-kpimon-go` | xApp | Go | 3690 | 4537 | 760 | 959 |
| `ric-app-rc` | xApp | C | 2451 | 3655 | 517 | 640 |

## Architectural styles observed

**1. Flat procedural pipeline (`ric-app-ad`, `ric-app-qp`, `nonrtric-rapp-healthcheck`).**
A handful of top-level modules (`main.py`, `database.py`, `ad_model.py`,
`processing.py`) with module-level globals and a `schedule`-driven loop. No
layering, no abstraction boundaries. `ad` and `qp` instantiate the generic
`Xapp` from `ricxappframe.xapp_frame`, pull state from SDL via `SDLWrapper`, and
run a pandas ML inference loop. Fast to read, hard to extend or unit-test in
isolation.

**2. Handler / Manager split with framework inheritance (`ric-app-hw-python`).**
The most structured OSC Python app. `HWXapp` wraps `RMRXapp` and registers
message-type callbacks. Two parallel package trees:
`handler/` (`_BaseHandler(ABC)`, `A1PolicyHandler`, `SubscriptionHandler`,
`HealthCheckHandler`) and `manager/` (`_BaseManager`, `A1PolicyManager`,
`SubscriptionManager`, `MetricManager`, `SdlManager`). Handlers react to inbound
RMR messages; managers drive outbound actions. This is the closest OSC comes to
design-pattern discipline: abstract base classes plus a registration mechanism,
but still no domain model, no ports, and no separation of O-RAN protocol from
business logic.

**3. Layered service (`nonrtric-plt-rappcatalogue`, `nonrtric-plt-rappmanager`).**
Platform components, not apps. The catalogue separates `configuration/`,
`repository/`, and a service entry point behind an OpenAPI contract
(`api/*.yaml`). `rappmanager` (Java/Spring) is a large CSAR onboarding and
lifecycle engine. Useful as the reference for how rApps are *packaged and
onboarded* (CSAR / TOSCA), which this template should target later.

## What every OSC app ships that this template historically lacked

These are operational scaffolding items present across the OSC apps and absent
from this template before the current upgrade. They are now the backbone of
Phases 4 to 6.

| Artifact | OSC apps that have it | This template |
| --- | --- | --- |
| `xapp-descriptor/config.json` onboarding contract (RMR `txMessages`/`rxMessages`, ports, registry image) | ad, qp, hw-python | Missing (rApp uses R1/SME registration instead — see note) |
| `tests/` + `conftest.py` unit tests | ad, qp, rappcatalogue | Added in Phase 4 |
| Sphinx docs (`docs/conf.py`) + `.readthedocs.yaml` | ad, qp, hw-python | Added in Phase 5 |
| CI workflows (`.github/workflows/gerrit-*`) | ad, qp, rappcatalogue | Added in Phase 4 (GitHub Actions) |
| Python packaging (`setup.py` / project metadata) | all Python apps | Added in Phase 4 (`pyproject.toml`) |
| Container release manifests (`releases/`, `container-tag.yaml`) | all | Partial (Dockerfile present) |

> **Note on the descriptor:** xApps onboard to the Near-RT RIC via
> `xapp-descriptor/config.json` and talk E2/A1 over the RMR message bus. rApps
> onboard to the Non-RT RIC via R1/SME registration and ICS data subscription,
> which this template already implements (`handlers/interfaces/r1.py`). The
> equivalent rApp packaging artifact is a CSAR bundle consumed by
> `rappmanager` (tracked in TODO under Later).

## What this template does better (and should keep)

OSC reference apps optimise for "works on the RIC", not for reuse or thesis
reproducibility. None of them use:

- A clear layered separation. This template adopts **MVC + handlers**
  (`models` / `controllers` / `views`, with O-RAN I/O in `handlers`) — the same
  shape as kpimon-go's entry + control + protocol-handlers + types, but typed
  and tested.
- The three BMW Lab SOP design patterns together (Adapter, Abstract Factory,
  Strategy). hw-python uses ABCs but not these patterns by name.
- A spec-traceable 3GPP parameter enum. OSC apps reference counters as bare
  strings scattered through code; this template centralises them in
  `ThreeGPPKpi` with TS section links.
- Frozen-dataclass value objects with typed interfaces.
- Any Intent-Based Networking contract layer.

Conclusion: keep the layered MVC structure and pattern discipline (it is the
thesis contribution and is strictly more maintainable), and bolt on the
operational scaffolding that OSC proves is necessary for a real deployment.

## Concrete takeaways feeding the upgrade

1. **E2 transport.** Every Near-RT RIC xApp uses `ricxappframe` + RMR. The
   template's `E2Client` ABC (`handlers/interfaces/e2.py`) should document
   `ricxappframe.xapp_frame.RMRXapp` as the canonical concrete transport, so the
   E2 RMR TODO has a clear reference implementation (hw-python's
   `SubscriptionManager` + `_BaseHandler.register_callback`).
2. **Config contract.** Ship a machine-readable descriptor so the app is
   onboardable. For the xApp profile, mirror `xapp-descriptor/config.json`; for
   the rApp profile, plan a CSAR bundle for `rappmanager`.
3. **Docs + tests + CI are table stakes**, not optional. OSC apps that omit them
   (healthcheck) are marked `DEPRECATED`. Phases 4 and 5 close this gap.
4. **Handler/Manager naming** in hw-python validates the template's
   `handlers/` choice; the template adds the `models` and `controllers` layers
   the OSC apps lack.
