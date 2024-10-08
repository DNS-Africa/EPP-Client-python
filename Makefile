PACKAGE:=epp-client

SHELL := /bin/bash

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

ifndef VERSION
		VERSION := 1.0.$(shell git rev-list --count HEAD)
endif

# Include the branch in the version name if it is default leave it blank
ifndef BRANCH
	BRANCH := $(shell git rev-parse --abbrev-ref HEAD )
	TAG_BRANCH := $(shell echo $(BRANCH) | grep -v '^-master' | grep -v '^-HEAD' | egrep -v '^gateway-3$$') # added eol to last grep
	TAG_BRANCH := $(strip $(TAG_BRANCH))
endif

DEV_TAG ?= dev
DEV_BRANCH_TAG ?= yes

ifndef DEV_BRANCH_TAG
	ifneq ($(BRANCH), )
		DEV_TAG := $(TAG_BRANCH:-%=%)
	endif
endif

PACKAGE ?= dams
export PACKAGE

PACKAGE_OWNER ?= dnsbusiness

ifdef DEV_BRANCH_TAG
	PACKAGE_NAME := $(PACKAGE_OWNER)/$(PACKAGE):$(DEV_TAG)
else
	PACKAGE_NAME := $(PACKAGE_OWNER)/$(PACKAGE)
endif

# linux/amd64 for Intel/AMD based linux/arm64 for M1/2 Mac or both
# DEV_PLATFORM=linux/amd64 make build push # for example
DEV_PLATFORM ?= linux/amd64

# Silence warning for buildx as we using multiplatform images.
BUILDX_NO_DEFAULT_LOAD=true
export BUILDX_NO_DEFAULT_LOAD

all: instructions push


instructions:
	@echo "Usage:"
	@echo " To create a local image for testing using the system platform"
	@echo "   make build"
	@echo " To create an image for testing on remote systems (default PLATFORM=linux/amd64, DEV_TAG=dev)"
	@echo "   make push"
	@echo "   DEV_TAG=python3.11 make push -> to make $(PACKAGE_OWNER)/$(PACKAGE):python3.11"
	@echo " To create a production image with a version tag (only linux/amd64)"
	@echo "   make publish"


# Builds and image and loads it into your local docker instance (default linux/amd64)
build:
	docker buildx build --load -t $(PACKAGE_OWNER)/$(PACKAGE):dev --build-arg SOURCE_BRANCH=$(VERSION) --output type=docker  .
	@echo "$(GREEN)# local docker image $(PACKAGE_OWNER)/$(PACKAGE):dev updated  $(RESET)"

# builds a dev image and pushes it to the dockerhub.com registry with the :dev tag (default linux/amd64)
push:
	docker buildx build --pull --push --platform $(DEV_PLATFORM) -t $(PACKAGE_OWNER)/$(PACKAGE):$(DEV_TAG) --build-arg SOURCE_BRANCH=$(VERSION) .
	@echo "$(GREEN)# This image is build with the tag :$(DEV_TAG) to use an alternate tag use the command as follows:$(RESET)"
	@echo "$(YELLOW) DEV_TAG=example make push"
	@echo "$(GREEN)# To get this image:$(RESET)"
	@echo "$(YELLOW) docker pull $(PACKAGE_OWNER)/$(PACKAGE):$(DEV_TAG)$(RESET)"


# pushes a version tag to github so that dockerhub is instructed to build a release image (Dockerhub only supports linux/amd64 currently)
publish:
	git tag $(VERSION)
	git push origin $(VERSION)
	@echo "$(GREEN)# To get this image:$(RESET)"
	@echo "$(YELLOW) docker pull $(PACKAGE_OWNER)/$(PACKAGE):$(VERSION)$(RESET)"
