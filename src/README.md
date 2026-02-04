# src/

This `src/` folder follows the **O-RAN SC nonrtric-rapp-healthcheck** convention:
- A runnable entrypoint at `src/main.py`
- Python dependencies listed in `src/requirements.txt`

At the same time, it provides a scalable structure for real rApps by using a
**Clean Architecture / Hexagonal (Ports & Adapters)** style under `src/rapp/`.

## Why this design fits rApps

rApps are typically **integration-heavy** (A1/REST calls, message buses, k8s, config maps, metrics).
A clean separation keeps your *policy/decision logic* testable and stable even as
external endpoints, SDKs, or deployment details change.

Key idea: **Dependency direction points inward**.
- The **domain/application** code never imports HTTP/A1/Kafka libraries.
- The **adapters** implement interfaces (“ports”) defined by the application.
- `main.py` is the **composition root** that wires everything together.

## Folder structure

- `main.py`
  - **Composition root**: loads settings, wires services/adapters, starts the server.
  - Keep it thin: no business logic.

- `rapp/config/`
  - Configuration parsing and validation.
  - `settings.py`: loads env vars (`RAPP_*` preferred; legacy supported).

- `rapp/domain/`
  - **Pure business logic** and data models.
  - `models.py`: dataclasses like `Health`, later `Kpi`, `Policy`, `Decision`.
  - `services.py`: logic like `HealthService`, later “evaluate KPIs → decide actions”.

- `rapp/application/`
  - **Use-cases** and **ports (interfaces)**.
  - `ports.py`: Protocol/ABC interfaces (e.g., `A1ClientPort`, `PolicyRepoPort`).
  - `usecases.py`: orchestrates domain services via ports.

- `rapp/adapters/`
  - Integrations to the outside world.
  - `http/`: HTTP handlers and server wiring.
  - (Future) `a1/`, `messaging/`, `db/`, `k8s/` adapters.

- `rapp/infrastructure/`
  - Logging, tracing, runtime utilities.
  - Keep infra helpers here so adapters stay small.

## Design patterns used (and where)

- **Ports & Adapters (Hexagonal)**
  - Ports are defined in `rapp/application/ports.py`.
  - Adapters (HTTP, A1, Kafka, DB) implement those ports.

- **Dependency Injection (manual)**
  - `src/main.py` constructs services and passes them into adapters.

- **Adapter pattern**
  - HTTP adapter translates HTTP ↔ use-case inputs/outputs.
  - Future: wrap A1 SDK/REST into a stable `A1ClientPort`.

- **Strategy pattern** (recommended for real rApps)
  - Put multiple decision algorithms under `domain/` and select via config.

- **Resilience patterns** (recommended)
  - Add timeouts/retries/circuit-breakers inside adapters calling external services.

## How to run locally

From repo root:

```bash
python3 src/main.py --port 8080
curl http://localhost:8080/health
```

Expected JSON includes `status`, `service`, `timestamp`.
