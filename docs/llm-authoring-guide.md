# LLM Authoring Guide — Generate an rApp/xApp from a PRD

> Purpose: a deterministic workflow for an LLM (Claude Code) to turn a completed
> `docs/PRD-TEMPLATE.md` into industrial-grade, spec-traceable source that
> satisfies the BMW Lab SOP and this template's architecture. Read this with
> `CLAUDE.md` (architectural rules) and `CONTEXT.md` (PRD) loaded.

## Why this template is LLM-friendly

The MVC + handlers layout gives an LLM a fixed place for every concern, so
generation is a fill-in-the-slots exercise rather than open-ended design:

| PRD section | Generates / edits | Layer |
| --- | --- | --- |
| Algorithm (Strategy) | `controllers/strategies.py` → `<Name>Strategy` | controllers |
| Inputs (3GPP params) | `models/parameters.py` (`ThreeGPPKpi`) + `models/kpi.py` | models |
| Outputs (decision) | `models/kpi.py` (`PolicyDecision` or custom enum) | models |
| O-RAN interfaces | `handlers/*.py` (reuse adapters) | handlers |
| Multi-vendor | `handlers/adapters/<vendor>/` (proprietary enum + map) | handlers |
| Intent (IBN) | `models/intent.py` (whitelist + resolve) | models |
| Control loop | `controllers/kpi_controller.py` (collect → analyze → decide) | controllers |
| Visualization | `views/grafana/*.json` (SMO Grafana) | views |
| Deployment env | `factories/<env>/` + `RAPP_PLATFORM` routing in `main.py` | factories |
| Config / secrets | `config/settings.py` + `helm/template-app/values.yaml` | config / helm |
| Tests | `tests/test_*.py` | tests |

## Generation workflow

1. **Sync context.** Read `CLAUDE.md`, `CONTEXT.md`, and (if present)
   `graphify-out/GRAPH_REPORT.md`. Do not re-read raw source when the graph
   answers a structure question.
2. **Validate the PRD.** Confirm every input parameter in PRD Section 4 is spec
   linked. If a counter is not in `ThreeGPPKpi`, add it to
   `models/parameters.py` first, with the TS link + section + page.
3. **Core first (Strategy + models).** Implement the algorithm as a
   `OptimizationStrategy` subclass. Pure logic, no I/O, no framework imports.
4. **Wire adapters, never reimplement them.** Reuse the existing
   `handlers/*` adapters for O1/A1/E2/R1/VES/TEIV. For a new vendor,
   add `handlers/adapters/<vendor>/` following `ericsson/__init__.py`.
5. **Compose in `main.py`.** Route `RAPP_PLATFORM` to the right factory; build
   the strategy and adapters; run the control loop.
6. **Tests for every pure unit.** Add `tests/test_*.py` covering the strategy,
   any new enum, and vendor mapping. Keep coverage ≥ 80% on models + controllers.
7. **Docs + Helm.** Update `CONTEXT.md` (PRD), `README.md` (usage), and
   `helm/template-app/values.yaml` (config/secrets) for new env vars.

## Hard rules the generator must enforce

These mirror `CLAUDE.md` "Architectural Rules" and the SOP. Violating any is a
review failure.

1. **No raw 3GPP string literals** in business logic. Always
   `ThreeGPPKpi.<MEMBER>.value`.
2. **Vendor mapping is adapter work.** Proprietary keys map to `ThreeGPPKpi`
   only inside `handlers/adapters/<vendor>/` — never in models or controllers.
3. **O-RAN protocols only.** The app never calls a simulator API directly;
   simulation is the BMW Lab TA rApp's job.
4. **Validate intents before resolving.** Call
   `IntentResolutionService.validate()` (whitelist + expiry + HMAC) before
   `resolve()`.
5. **Spec-traceability.** Every parameter reference in code, docstrings, and the
   System Parameters table links to the spec ZIP with section and page.
6. **Sphinx/RST docstrings** on every public class and function
   (`:param:`/`:return:`/`:raises:`).

## Definition of done (run before handover)

```bash
ruff check src tests examples && ruff format --check src tests examples
mypy src
pytest                          # 80% floor on models + controllers
sphinx-build -b html docs docs/_build/html -W
helm lint helm/template-app && helm template rapp helm/template-app --set secrets.RAPP_INTENT_SECRET=x
RAPP_PLATFORM=mock PYTHONPATH=src python src/main.py   # then curl :8080/health
graphify update .               # refresh the knowledge graph (free, AST-only)
```

A change is done only when all of the above pass and the four session files
(`CLAUDE.md`, `CONTEXT.md`, `MEMORY.md`, `TODO.md`) are reconciled.
