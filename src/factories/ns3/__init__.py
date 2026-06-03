"""ns-3 simulation platform — guidance stub.

For ns-3 simulation, use :class:`factories.osc.OscPlatformFactory` pointed at
the O-RAN interfaces provided by ns-O-RAN or the BMW Lab TA rApp:

    factory = OscPlatformFactory(
        sme_base_url=os.environ["RAPP_SME_BASE_URL"],   # TA rApp / ns-O-RAN endpoint
        ics_base_url=os.environ["RAPP_ICS_BASE_URL"],
        ...
    )

Rationale
    The generic rApp communicates exclusively through O-RAN ALLIANCE protocols
    (O1/A1/R1/E2).  ns-3 simulation lifecycle (start/stop scenarios,
    configure UE mobility) is orchestrated by the BMW Lab TA rApp
    (github.com/bmw-ece-ntust/nonrtric-rapp-test-automation), which exposes
    O-RAN standard interfaces toward the rApp and ns-3 / VIAVI proprietary
    APIs on the other side.  The rApp never calls simulator APIs directly.

TA rApp
    https://github.com/bmw-ece-ntust/nonrtric-rapp-test-automation

ns-O-RAN (ns-3 E2 node integration)
    https://openrangym.com/ran-frameworks/ns-o-ran
"""
