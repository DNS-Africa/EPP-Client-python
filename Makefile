.PHONY: build push publish

SHELL := /bin/bash

# Default target
.DEFAULT_GOAL := instructions

PACKAGE := epp-client
PACKAGE_OWNER ?= dnsbusiness

# define standard colors
ifneq (,$(findstring xterm,${TERM}))
	BLACK        := $(shell tput -Txterm setaf 0)
	RED          := $(shell tput -Txterm setaf 1)
	GREEN        := $(shell tput -Txterm setaf 2)
	YELLOW       := $(shell tput -Txterm setaf 3)
	LIGHTPURPLE  := $(shell tput -Txterm setaf 4)
	PURPLE       := $(shell tput -Txterm setaf 5)
	BLUE         := $(shell tput -Txterm setaf 6)
	WHITE        := $(shell tput -Txterm setaf 7)
	RESET := $(shell tput -Txterm sgr0)
else
	BLACK        := ""
	RED          := ""
	GREEN        := ""
	YELLOW       := ""
	LIGHTPURPLE  := ""
	PURPLE       := ""
	BLUE         := ""
	WHITE        := ""
	RESET        := ""
endif

# Source version lives in the VERSION file (one line: X.Y.Z).
VERSION_FILE := VERSION
SOURCE_VERSION := $(shell cat $(VERSION_FILE) 2>/dev/null | tr -d "[:space:]")

# Image tag alias: dev on the default branch, otherwise the branch name with
# / and - replaced by _. Override with BRANCH=<name> (e.g. BRANCH=main).
# NOTE: never expand $(BRANCH) inside a $(shell ...) here — GNU Make 3.81 on
# macOS eats the $ of the $' quoting bash would need; it is expanded in the
# recipe instead, where the shell quoting is safe.
BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)

# linux/amd64 for Intel/AMD based linux/arm64 for M1/2 Mac or both
# DEV_PLATFORM=linux/amd64 make push # for example
DEV_PLATFORM ?= linux/amd64

# Silence warning for buildx as we using multiplatform images.
BUILDX_NO_DEFAULT_LOAD=true
export BUILDX_NO_DEFAULT_LOAD

# This repo is a manual EPP test client: there is NO test suite by design, so
# publish has no test gate. `python3 epp.py -t templates/domain_info.xml`
# renders a command without connecting.

instructions:
	@echo "Usage:"
	@echo " To create a local image for testing using the system platform"
	@echo "   make build"
	@echo " To build and push a dev/beta image, tagged from the current branch"
	@echo "   make push                     -> $(PACKAGE_OWNER)/$(PACKAGE):<dev|branch> (now: $(BRANCH))"
	@echo "   BRANCH=feature/foo make push  -> $(PACKAGE_OWNER)/$(PACKAGE):feature_foo"
	@echo "   The baked-in version is $(SOURCE_VERSION)-<alias>_<timestamp>; no git state is touched"
	@echo " To release (bump VERSION, commit, tag, push; CI builds the release image)"
	@echo "   make publish                  -> bump build/patch, e.g. $(SOURCE_VERSION) -> next"
	@echo "   make publish BUMP=minor|major | make publish NEXT=x.y.z | make publish VERSION_BUMP=false"
	@echo " (make with no target shows this and builds nothing)"

# Builds an image and loads it into your local docker instance (default linux/amd64)
build:
	@[ -n "$(SOURCE_VERSION)" ] || { echo "$(RED)Could not read version from $(VERSION_FILE)$(RESET)"; exit 1; }
	docker buildx build --load -t $(PACKAGE_OWNER)/$(PACKAGE):dev --build-arg SOURCE_BRANCH=$(SOURCE_VERSION) --output type=docker  .
	@echo "$(GREEN)# local docker image $(PACKAGE_OWNER)/$(PACKAGE):dev updated  $(RESET)"

# Builds a dev/beta image and pushes it to dockerhub.com, tagged with the branch
# alias (dev on main/master). Image only: no commits, no tags.
push:
	@[ -n "$(SOURCE_VERSION)" ] || { echo "$(RED)Could not read version from $(VERSION_FILE)$(RESET)"; exit 1; }
	@STAMP=$$(date +%Y%m%d%H%M); \
	case "$(BRANCH)" in main|master) ALIAS=dev ;; *) ALIAS="$$(printf '%s' "$(BRANCH)" | tr '/-' '__')" ;; esac; \
	BUILD_VERSION="$(SOURCE_VERSION)-$${ALIAS}_$$STAMP"; \
	echo "$(GREEN)# building $(PACKAGE_OWNER)/$(PACKAGE):$$ALIAS (version $$BUILD_VERSION)$(RESET)"; \
	docker buildx build --pull --push --platform $(DEV_PLATFORM) -t $(PACKAGE_OWNER)/$(PACKAGE):$$ALIAS --build-arg SOURCE_BRANCH=$$BUILD_VERSION . ; \
	echo "$(GREEN)# This image is built with the tag :$$ALIAS (from branch $(BRANCH))$(RESET)"; \
	echo "$(GREEN)# To get this image:$(RESET)"; \
	echo "$(YELLOW) docker pull $(PACKAGE_OWNER)/$(PACKAGE):$$ALIAS$(RESET)"

# Full release: bump VERSION, commit the bump, tag the bare version and push
# branch + tag; CI builds the release image from the tag. There is no test gate
# (no test suite in this repo). Publish from the main checkout on the default
# branch, never from a worktree.
publish:
	@test -z "$$(git status --porcelain --untracked-files=no)" || { echo "$(RED)Working tree is not clean — commit or stash first$(RESET)"; exit 1; }
	@VERSION="$$(cat $(VERSION_FILE) | tr -d '[:space:]')"; \
	[ -n "$$VERSION" ] || { echo "$(RED)Could not read version from $(VERSION_FILE)$(RESET)"; exit 1; }; \
	echo "$(GREEN)Current version: $$VERSION$(RESET)"; \
	if [ -n "$(NEXT)" ]; then \
		NEXT_VERSION="$(NEXT)"; \
		case "$$NEXT_VERSION" in [0-9]*.[0-9]*.[0-9]*) ;; *) echo "$(RED)ERROR: version '$$NEXT_VERSION' is not X.Y.Z — refusing to publish.$(RESET)"; exit 1;; esac; \
	elif [ "$(BUMP)" = "major" ]; then \
		MAJOR="$$(echo "$$VERSION" | cut -d. -f1 | sed 's/^0*//;s/^$$/0/')"; \
		NEXT_VERSION="$$((MAJOR+1)).0.0"; \
	elif [ "$(BUMP)" = "minor" ]; then \
		MAJOR="$$(echo "$$VERSION" | cut -d. -f1)"; \
		MINOR="$$(echo "$$VERSION" | cut -d. -f2 | sed 's/^0*//;s/^$$/0/')"; \
		NEXT_VERSION="$$MAJOR.$$((MINOR+1)).0"; \
	elif [ "$(BUMP)" = "build" ] || [ "$(BUMP)" = "patch" ] || [ -z "$(BUMP)" ]; then \
		MAJOR="$$(echo "$$VERSION" | cut -d. -f1)"; \
		MINOR="$$(echo "$$VERSION" | cut -d. -f2 | sed 's/^0*//;s/^$$/0/')"; \
		BUILD="$$(echo "$$VERSION" | cut -d. -f3 | sed 's/^0*//;s/^$$/0/')"; \
		NEXT_VERSION="$$MAJOR.$$MINOR.$$((BUILD+1))"; \
	else \
		echo "$(RED)Unknown BUMP value: $(BUMP) (use: build, minor, major)$(RESET)"; \
		exit 1; \
	fi; \
	case "$$NEXT_VERSION" in [0-9]*.[0-9]*.[0-9]*) ;; *) echo "$(RED)ERROR: version '$$NEXT_VERSION' is not X.Y.Z — refusing to publish.$(RESET)"; exit 1;; esac; \
	if [ "$(VERSION_BUMP)" = "false" ]; then \
		echo "$(YELLOW)VERSION_BUMP=false — skipping version bump and commit$(RESET)"; \
	else \
		echo "$(GREEN)Bumping $(VERSION_FILE): $$VERSION → $$NEXT_VERSION$(RESET)"; \
		printf '%s\n' "$$NEXT_VERSION" > $(VERSION_FILE); \
		NEWV="$$(cat $(VERSION_FILE) | tr -d '[:space:]')"; \
		[ "$$NEWV" = "$$NEXT_VERSION" ] || { echo "$(RED)Version bump failed: expected $$NEXT_VERSION, got $$NEWV$(RESET)"; exit 1; }; \
		git add $(VERSION_FILE); \
		git commit -m "release: version $$NEXT_VERSION"; \
	fi; \
	echo "$(YELLOW)No tests to run (this repo has no test suite by design)$(RESET)"; \
	if ! git show-ref --tags --verify "refs/tags/$$NEXT_VERSION" >/dev/null 2>&1; then \
		git tag $$NEXT_VERSION; \
	else \
		echo "$(YELLOW)Tag $$NEXT_VERSION already exists — keeping it (no -f)$(RESET)"; \
	fi; \
	git push origin HEAD; \
	git push origin $$NEXT_VERSION; \
	echo "$(GREEN)✓ Published $$NEXT_VERSION — commit and tag pushed, CI release build triggered$(RESET)"; \
	echo "$(YELLOW) docker pull $(PACKAGE_OWNER)/$(PACKAGE):$$NEXT_VERSION$(RESET)"
