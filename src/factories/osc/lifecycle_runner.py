"""rApp lifecycle management within the O-RAN SC Non-RT RIC (SME + ICS)."""

from __future__ import annotations

import logging

from factories import ScenarioRunner
from handlers.interfaces.r1 import ICSAdapter, SMEAdapter

_log = logging.getLogger(__name__)


class OscLifecycleRunner(ScenarioRunner):
    """Manages the rApp lifecycle within the O-RAN SC Non-RT RIC.

    On :meth:`start`, registers the rApp with SME and subscribes to all
    configured ICS data types.  On :meth:`stop`, cancels subscriptions and
    deregisters from SME in reverse order for a clean shutdown.

    :param sme: Configured :class:`~handlers.interfaces.r1.SMEAdapter` instance.
    :param ics: Configured :class:`~handlers.interfaces.r1.ICSAdapter` instance.
    :param ics_data_types: List of ICS data type IDs to subscribe to
        (e.g. ``["PM_REPORT_CELL_LEVEL"]``).

    :Example:

        >>> runner = OscLifecycleRunner(sme, ics, ["PM_REPORT_CELL_LEVEL"])
        >>> runner.start()   # rApp is now registered and receiving data
        >>> runner.stop()    # graceful shutdown: unsubscribe then deregister
    """

    def __init__(
        self,
        sme: SMEAdapter,
        ics: ICSAdapter,
        ics_data_types: list[str],
    ) -> None:
        self._sme = sme
        self._ics = ics
        self._ics_data_types = ics_data_types

    def start(self) -> None:
        """Register with SME and subscribe to all configured ICS data types.

        :raises handlers.interfaces.r1.R1SMEError: If SME registration fails.
        :raises handlers.interfaces.r1.R1ICSError: If any ICS subscription fails.
        """
        _log.info("OscLifecycleRunner: starting")
        self._sme.register()
        for data_type in self._ics_data_types:
            self._ics.subscribe(data_type)
        _log.info("OscLifecycleRunner: started — subscribed to %s", self._ics_data_types)

    def stop(self) -> None:
        """Cancel all ICS subscriptions and deregister from SME.

        ICS errors are logged but not re-raised so that SME deregistration
        always runs even when some subscriptions fail to cancel.
        """
        _log.info("OscLifecycleRunner: stopping")
        self._ics.unsubscribe_all()
        self._sme.deregister()
        _log.info("OscLifecycleRunner: stopped")
