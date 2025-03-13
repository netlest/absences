IMAGE_NAME=absences
SHELL=/bin/bash

all: help

.PHONY: help
help: Makefile
	@echo "Choose a command run:"
	@(sed -n "s/^## //p" Makefile | column -t -s ":" | sed -e "s/^/  /")

## init-python: Setup Python virtual environment and install dependencies
.PHONY: init-python
init-python:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt

## init-db: Initialize the database
.PHONY: init-db
init-db:
	flask init-db

## clean: Remove Python virtual environment
.PHONY: clean
clean:
	rm -rf venv

## build: Build the Docker image
.PHONY: build
build:
	docker build -t ${IMAGE_NAME}:latest .

# compose-up: Build the Docker image
.PHONY: compose-up
compose-up:
	docker compose up -d

## remove-image: Remove Docker image
.PHONY: docker-stop
docker-stop:
	docker stop ${IMAGE_NAME}

## remove-image: Remove Docker image
.PHONY: docker-rm
docker-rm:
	docker rm ${IMAGE_NAME}

## remove-unused-images: Remove unused Docker images
.PHONY: remove-unused-images
remove-unused-images:
	docker image prune -a -f

## remove-image: Remove Docker image
.PHONY: remove-image
remove-image:
	docker rmi ${IMAGE_NAME}:latest

## list-images: List Docker images
.PHONY: list-images
list-images:
	docker images

## docker-cleanup: Cleanup docker stack
.PHONY: docker-cleanup
docker-cleanup:
	$(MAKE) docker-stop
	$(MAKE) docker-rm
	$(MAKE) remove-image
	$(MAKE) remove-unused-images
	$(MAKE) list-images

## docker-init: Containerize app
.PHONY: docker-init
docker-init:
	$(MAKE) build
	$(MAKE) compose-up

