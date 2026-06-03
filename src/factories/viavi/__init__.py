"""VIAVI RSG simulation platform — guidance stub.

For VIAVI RSG simulation, use :class:`factories.osc.OscPlatformFactory`
pointed at VIAVI's native O-RAN interfaces:

    factory = OscPlatformFactory(
        sme_base_url=os.environ["RAPP_SME_BASE_URL"],   # VIAVI Non-RT RIC endpoint
        ics_base_url=os.environ["RAPP_ICS_BASE_URL"],   # VIAVI ICS endpoint
        ...
    )

Rationale
    VIAVI RSG provides a fully functional O-RAN interface layer (O1 NETCONF,
    A1 policy, E2 KPM/RC) natively.  Simulation lifecycle (start/stop test
    scenarios, configure UE profiles) is the responsibility of the BMW Lab
    TA rApp (github.com/bmw-ece-ntust/nonrtric-rapp-test-automation), which
    calls VIAVI's proprietary REST API (``/sba/tests/run``) and is not part
    of the generic rApp.  The rApp uses VIAVI exactly as it would use a real
    gNB — through O-RAN standard protocols only.

TA rApp
    https://github.com/bmw-ece-ntust/nonrtric-rapp-test-automation

VIAVI RIC Test (RSG)
    https://www.viavi.com/en-us/products/ric-test
"""
