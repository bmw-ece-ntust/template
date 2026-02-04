# Containerized (Docker + Helm) Tutorial

This repo template is intended to be containerized for reproducible research execution and easy student onboarding.

## Prerequisites

- Docker Desktop (macOS/Windows) or Docker Engine (Linux)
- `kubectl` (for Kubernetes steps)
- `helm` (v3)
- A Kubernetes cluster for local testing (pick one):
  - **kind** (recommended for laptops)
  - minikube
  - k3d

## 1) Docker: build and run locally

### Build

From the repo root:

```bash
docker build -t template-app:dev .
```

### Run

```bash
docker run --rm -p 8080:8080 -e SERVICE_NAME=template-app template-app:dev
```

Recommended (rApp-style env var prefix):

```bash
docker run --rm -p 8080:8080 -e RAPP_SERVICE_NAME=template-app -e RAPP_PORT=8080 template-app:dev
```

### Verify

```bash
curl http://localhost:8080/health
```

Expected (example):

```json
{"status":"OK","service":"template-app","timestamp":1738540000}
```

## 2) Kubernetes: load the image into a local cluster (kind example)

If you use **kind**, images built locally are not automatically available inside the cluster.

```bash
kind create cluster
kind load docker-image template-app:dev
```

## 3) Helm: deploy the chart

This repo includes a minimal Helm chart at
[`test/usecases/healthcheck/scriptversion/helm/template-app`](../test/usecases/healthcheck/scriptversion/helm/template-app).

### Lint and render templates

These do not require a cluster:

```bash
helm lint ./test/usecases/healthcheck/scriptversion/helm/template-app
helm template template-app ./test/usecases/healthcheck/scriptversion/helm/template-app \
  --set image.repository=template-app \
  --set image.tag=dev
```

### Install into a cluster

```bash
helm install template-app ./test/usecases/healthcheck/scriptversion/helm/template-app \
  --set image.repository=template-app \
  --set image.tag=dev
```

### Port-forward and test

```bash
kubectl port-forward svc/template-app 8080:8080
curl http://localhost:8080/health
```

### Uninstall

```bash
helm uninstall template-app
```

## 4) Helm: package the chart (share with students)

To publish or share a packaged chart artifact:

```bash
mkdir -p dist/helm
helm package ./test/usecases/healthcheck/scriptversion/helm/template-app -d dist/helm
```

If you want a simple static Helm repo (e.g., GitHub Pages), generate an index:

```bash
helm repo index dist/helm
```

## Notes for O-RAN rApps/xApps

- Treat an **xApp/rApp** as a deployable service with:
  - a container image
  - a Helm chart (values for image, endpoints, credentials, feature flags)
  - a clear `/health` endpoint and structured logs
- Extend the chart when your project needs dependencies (examples):
  - Kafka, Redis, Prometheus/Grafana
  - A1/E2 endpoints, TLS secrets, config maps for policy files

Next step suggestion: add an `Ingress` and/or `ServiceAccount + RBAC` section once the app needs cluster API access.
