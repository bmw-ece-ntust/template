from __future__ import annotations

import logging


def configure_logging() -> None:
    """Basic structured-ish logging.

    Real rApps often emit JSON logs; keep this minimal for the template.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
