# test/

This folder mirrors the common O-RAN SC rApp layout where **demo/test harness scripts** live under `test/`.

Typical contents for an rApp repo:
- `start.sh`: bring up required dependencies (e.g., simulators, policy management service) for local testing
- `stop.sh`: stop/cleanup dependencies
- `usecases/`: optional, one subfolder per use case with manifests/charts/testdata

This template intentionally ships **placeholders** here. Adapt to your project’s dependencies.
