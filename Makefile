#!make
include .local.env
export

all: | setup start

setup: .venv setup-protobuf setup-clustering setup-embedding setup-load-balancer setup-segmentation setup-tracking

.venv:
	python -m venv .venv

setup-protobuf:
	$(info Building protobuf files)
	cd protobuf && $(MAKE)

setup-clustering:
	$(info Building clustering)
	cd clustering && $(MAKE)

setup-embedding:
	$(info Building embedding)
	cd embedding && $(MAKE)

setup-load-balancer: setup-protobuf
	$(info Building load-balancer)
	cd load-balancer && $(MAKE)

setup-segmentation:
	$(info Building segmentation)
	cd segmentation && $(MAKE)

setup-tracking:
	$(info Building tracking)
	cd tracking && $(MAKE)

start-clustering: setup-clustering
	$(info Starting clustering)
	$(MAKE) -C clustering start

start-embedding: setup-embedding
	$(info Starting embedding)
	$(MAKE) -C embedding start

start-load-balancer: setup-load-balancer
	$(info Starting load-balancer)
	$(MAKE) -C load-balancer start

start-segmentation: setup-segmentation
	$(info Starting segmentation)
	$(MAKE) -C segmentation start

start-tracking: setup-tracking
	$(info Starting tracking)
	$(MAKE) -C tracking start

start-traefik-db:
	$(info Starting traefik and db)
	docker-compose -f docker-compose-traefik-db.yml up

start:
	$(info Starting all services)
	$(MAKE) -j6 start-clustering start-embedding start-load-balancer start-segmentation start-tracking start-traefik-db

clean:
	rm -rf .venv
	cd protobuf && $(MAKE) clean
	cd clustering && $(MAKE) clean
	cd embedding && $(MAKE) clean
	cd load-balancer && $(MAKE) clean
	cd segmentation && $(MAKE) clean
	cd tracking && $(MAKE) clean

.PHONY: all setup setup-protobuf setup-clustering setup-embedding setup-load-balancer setup-segmentation setup-tracking start-clustering start-embedding start-load-balancer start-segmentation start-tracking start-traefik-db start clean