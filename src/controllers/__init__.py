"""Controllers (C) — orchestration and decision algorithms.

Controllers wire the handlers (O-RAN I/O) to the models, run the control loop,
and select an optimization :mod:`~controllers.strategies` (Strategy pattern).
They contain no protocol/transport code; that lives in :mod:`handlers`.
"""
