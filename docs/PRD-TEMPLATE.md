# PRD Template — <rApp / xApp Name>

> Fill every section before writing code. This PRD is the design contract: the
> generated source must implement exactly what is described here (BMW Lab SOP
> source-code-guide Section 1, "Design-First"). Copy this file to `CONTEXT.md`
> for a new project and complete it. An LLM uses this document, plus
> `docs/llm-authoring-guide.md`, to generate the implementation.

## 1. Identity

- **Name:**
- **Type:** rApp (Non-RT RIC) | xApp (Near-RT RIC)
- **Objective (one sentence):**
- **Owner / author:**

## 2. Problem and contribution

- **Background:** What RAN problem does this address?
- **Contribution:** What is the novel algorithm or capability (the thesis core)?

## 3. O-RAN interfaces used

Tick the interfaces this app consumes or produces, and the adapter that backs
each (see `src/handlers/`).

| Interface | Used? | Direction | Adapter |
| --- | --- | --- | --- |
| O1 (config/PM via SDNC) | | in/out | `o1.py` |
| A1 (policy) | | out (rApp) / in (xApp) | `a1.py` |
| E2 SM-KPM (metrics) | | in (xApp) | `e2.py` |
| E2 SM-RC (control) | | out (xApp) | `e2.py` |
| R1 SME (lifecycle) | | both (rApp) | `r1.py` |
| R1 ICS (data subscription) | | in (rApp) | `r1.py` |
| VES (O1 events) | | in | `ves.py` |
| TEIV (topology) | | in | `teiv.py` |

## 4. Inputs — System Parameters table (SOP Section 8)

Every parameter must be spec-traceable. Use `ThreeGPPKpi` members; add new ones
to `src/models/parameters.py` with a spec link before use.

| Category | Parameter | Type | Unit | Standard | Section | Page / § | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E2 KPM Input | `DRB.PrbUtilDL` | float | ratio | TS 28.552 | §5.1.1.12.1 | Table 5.1.1.12.1-1, p.47 | DL PRB utilization |
| | | | | | | | |

## 5. Outputs

- **Decision type:** `PolicyDecision` (ACTIVE/SLEEP/HANDOVER) | custom enum (define it)
- **Where it goes:** A1 policy | E2 RC control | O1 config write

## 6. Algorithm (Strategy)

- **Strategy class name:** `<Name>Strategy(OptimizationStrategy)`
- **Rule / model:** Describe the decision logic. Threshold-based, ML, or NIM.
- **Pseudocode:**

```
evaluate(kpis) -> PolicyDecision:
    ...
```

## 7. Multi-vendor scope

- **Vendors to support:** e.g. ericsson, nokia
- **New proprietary parameters?** If yes, list them; they go in a
  `src/factories/<vendor>/` Abstract Factory (selected by `RAPP_PLATFORM`) with a
  proprietary enum + `VendorParameterMap` → `ThreeGPPKpi` inside its analyzer.

## 8. Intent-Based Networking (optional)

- **Intent types consumed:** (must be in the `IntentType` whitelist)
- **Constraints:** parameter / operator / threshold tuples

## 9. Deployment

- **Platform:** mock | osc | physical (`RAPP_PLATFORM`)
- **Config (RAPP_* env):** list non-default values
- **Secrets:** `RAPP_INTENT_SECRET`, `NVIDIA_API_KEY`, registry pull token
- **Resources:** CPU / memory requests and limits

## 10. Diagrams (required before coding)

- [ ] Flowchart (main control loop)
- [ ] Class diagram (matches `src/` classes)
- [ ] Message Sequence Chart (per use case)

## 11. Evaluation

- **Metrics:** how success is measured
- **Test plan:** mock unit tests + BMW Lab TA rApp integration

## 12. Known issues / out of scope (SOP Section 7.3)

| Issue | Severity | Status | Workaround |
| --- | --- | --- | --- |
| | | | |
