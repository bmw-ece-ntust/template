"""rApp template package.

This package is intentionally small but structured to scale:
- domain/: pure business logic and data models
- application/: use-cases and port (interface) definitions
- adapters/: integrations (HTTP, A1, messaging, etc.)
- infrastructure/: logging, runtime utilities

The entrypoint remains `src/main.py` as a thin composition root.
"""
