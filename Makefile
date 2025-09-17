SHELL := /bin/bash

# Defaults
REGISTRY ?= 192.168.8.84
PROJECT  ?= library

# Load per-dev overrides
-include make.local

# Normalize (strip all leading/trailing whitespace from values)
override HARBOR_USER    := $(strip $(HARBOR_USER))
override HARBOR_PASSWORD:= $(strip $(HARBOR_PASSWORD))
override IMAGE          := $(strip $(IMAGE))
override TAG            := $(strip $(TAG))

# Require vars
ifeq ($(HARBOR_USER),)
  $(error Set HARBOR_USER in make.local)
endif
ifeq ($(HARBOR_PASSWORD),)
  $(error Set HARBOR_PASSWORD in make.local)
endif
ifeq ($(IMAGE),)
  $(error Set IMAGE in make.local)
endif
ifeq ($(TAG),)
  $(error Set TAG in make.local)
endif

# Export creds so the script sees them
export HARBOR_USER
export HARBOR_PASSWORD

.PHONY: build-push
build-push:
	@echo "Pushing $(REGISTRY)/$(PROJECT)/$(IMAGE):$(TAG)"
	./scripts/image-build-push.sh \
	  --registry "$(REGISTRY)" --project "$(PROJECT)" \
	  --image "$(IMAGE)" --tag "$(TAG)" --context .
