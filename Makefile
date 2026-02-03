SHELL := /bin/bash

# Defaults
REGISTRY ?= 192.168.8.84
PROJECT  ?= bmw-ece-ntust

# Load per-dev overrides
-include make.local

# Normalize (strip all leading/trailing whitespace from values)
override HARBOR_USER    := $(strip $(HARBOR_USER))
override HARBOR_PASSWORD:= $(strip $(HARBOR_PASSWORD))
override IMAGE          := $(strip $(IMAGE))
override TAG            := $(strip $(TAG))

# Export creds so the script sees them (may be empty; validated per-target).
export HARBOR_USER
export HARBOR_PASSWORD

.PHONY: help
help:
	@printf "%s\n" \
	  "Targets:" \
	  "  make build-push      Build and push to Harbor (requires make.local)" \
	  "  make docker-build    Build the local Docker image" \
	  "  make docker-run      Run the local Docker image" \
	  "  make helm-lint       Lint the Helm chart" \
	  "  make helm-template   Render Helm templates (no cluster needed)"

.PHONY: build-push
build-push:
	@test -n "$(HARBOR_USER)" || (echo "Set HARBOR_USER in make.local" >&2; exit 2)
	@test -n "$(HARBOR_PASSWORD)" || (echo "Set HARBOR_PASSWORD in make.local" >&2; exit 2)
	@test -n "$(IMAGE)" || (echo "Set IMAGE in make.local" >&2; exit 2)
	@test -n "$(TAG)" || (echo "Set TAG in make.local" >&2; exit 2)
	@echo "Pushing $(REGISTRY)/$(PROJECT)/$(IMAGE):$(TAG)"
	./scripts/image-build-push.sh \
	  --registry "$(REGISTRY)" --project "$(PROJECT)" \
	  --image "$(IMAGE)" --tag "$(TAG)" --context .

.PHONY: docker-build
docker-build:
	docker build -t template-app:dev .

.PHONY: docker-run
docker-run:
	docker run --rm -p 8080:8080 -e SERVICE_NAME=template-app template-app:dev

.PHONY: helm-lint
helm-lint:
	helm lint ./helm/template-app

.PHONY: helm-template
helm-template:
	helm template template-app ./helm/template-app
