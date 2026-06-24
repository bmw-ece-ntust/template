# BMW Lab SOP Review — source-code-guide.md

> Assessment of `bmw-ece-ntust/SOP/source-code-guide.md` against industrial-grade
> Python and O-RAN practice, produced while upgrading this template. Verdict:
> the SOP is strong on design discipline and spec-traceability but under-specifies
> automated quality enforcement and modern packaging. Below: what to keep, what
> to add, what to refine, and what to relax.

## Verdict

The SOP is above average for an academic lab: design-first artifacts (Section 1),
the three design patterns (Section 3), Sphinx/Doxygen docstrings (Section 4),
production-readiness checks (Section 7), and the parameter spec-traceability
convention (Section 8, the page-and-section rule) are genuinely excellent and
rare. The main weakness is that quality is asserted but not enforced: nothing
runs a linter, type checker, or test-coverage gate, so compliance depends on
reviewer diligence.

## Strengths (keep as-is)

1. **Design-first ordering** (flowchart → class diagram → system parameters)
   before code. Prevents architecture-by-accident.
2. **Spec-traceability** (Section 8). The "link every parameter to spec ZIP +
   section + page" rule is the single best part; it makes claims verifiable by
   future students and LLMs. Keep verbatim.
3. **Production-readiness checklist** (Section 7): pullable images, submodule
   init, mandatory Known Issues, endpoint-name consistency, secrets in
   `.env.example`. These map to real handover failures.
4. **Three design patterns** (Adapter / Abstract Factory / Strategy) give a
   shared vocabulary and keep the thesis algorithm separable.

## Gaps — recommend ADDING

| # | Gap | Recommended SOP addition |
| --- | --- | --- |
| 1 | No automated quality gates | Mandate `ruff` (lint+format), `mypy`, and `pytest` with a coverage floor (e.g. 80% on core + domain). Docstrings (Section 4) are required but unchecked. |
| 2 | No CI requirement | Require a CI workflow (GitHub Actions / Gerrit) running lint → type → test → docs build on every PR. Every OSC reference app has this; the SOP does not ask for it. |
| 3 | No pre-commit | Recommend `.pre-commit-config.yaml` (ruff, mypy, trailing-whitespace) so issues are caught before commit. |
| 4 | No modern packaging | Section 5 shows only `requirements.txt`. Add `pyproject.toml` (PEP 621) with pinned deps, dev extras, and tool config; pin runtime deps for reproducible handover. |
| 5 | Weak testing mandate | Section 5 lists a `tests/` folder but Section gives no testing rules. Add: unit tests for pure logic, a coverage floor, and integration delegated to the TA rApp. |
| 6 | No 3GPP enum rule | Section 8 mandates naming + linking but allows raw string literals. Mandate a `ThreeGPPKpi`-style enum so counters are typo-proof and testable. |
| 7 | Vendor adapters under-specified | Section 3.1 shows one `GnbTelemetryAdapter`. For multi-vendor O-RAN, prescribe a per-vendor Abstract Factory `factories/<vendor>/` (selected by `RAPP_PLATFORM`) with a proprietary-parameter enum + a `VendorParameterMap` to `ThreeGPPKpi` inside its analyzer; keep `handlers/` O-RAN-standard only. |
| 8 | No IBN / intent security | Add an optional section for contract-based Intent-Based Networking (RFC 9315): whitelist + expiry + HMAC validation before resolution. |
| 9 | No Helm / packaging detail | Section 7.1 covers images but not chart structure. Add a Helm section: config/secret separation, `securityContext`, resource requests/limits, and CSAR/TOSCA onboarding for the rApp Manager. |

## Refinements — recommend CHANGING

1. **Allow a layered layout.** Section 5 prescribes a flat `src/adapters/`.
   Permit (and ideally recommend) a layered structure such as **MVC + handlers**
   (`src/{models,controllers,views,handlers,factories,config}`, the shape this
   template uses and the shape of OSC `ric-app-kpimon-go`). It is strictly more
   testable, as this template's 98% models+controllers coverage shows, and OSC
   apps that stay flat (ad, qp) are hard to unit-test.
2. **Factories key on deployment environment, not simulator vendor.** Section 3.2
   / Section 5 list `ns3` / `viavi` / `physical` factories. Since simulation is
   driven by the BMW Lab TA rApp over O-RAN interfaces, the real discriminator is
   `mock` / `osc` / `physical`. Reframing removes dead simulator-specific stub
   code and matches how deployment actually varies.

## Reductions — recommend RELAXING / REMOVING

1. **Make `simulation/` optional for product repos.** Section 5 mandates a
   `simulation/` folder for scripts, raw data, and notebooks. For a clean,
   deployable rApp product where testing is delegated to the TA rApp, this folder
   is dead weight (this template removed it). Recommend: required for research
   repos, optional for product/template repos, with the rationale documented.
2. **Drop mandatory `ns3/` and `viavi/` factory folders.** They become guidance
   stubs once factories key on deployment environment (see Refinement 2),
   reducing boilerplate every project must carry.

## Proposed SOP edit checklist

- [ ] Add "Section 9: Automated Quality Gates" (ruff, mypy, pytest + coverage, CI, pre-commit).
- [ ] Add "Section 10: Packaging" (`pyproject.toml`, dependency pinning, Helm, CSAR).
- [ ] Extend Section 3.1 with the per-vendor adapter folder + proprietary enum pattern.
- [ ] Extend Section 8 with a mandatory `ThreeGPPKpi` enum rule.
- [ ] Add an optional "Intent-Based Networking" section (validate-before-resolve).
- [ ] Soften Section 5: hexagonal layout allowed; `simulation/` optional for product repos; factories keyed on environment.
