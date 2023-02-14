#!make
include .local.env
export

all: setup start

setup: setup-protobuf setup-clustering setup-embedding setup-load-balancer setup-segmentation setup-tracking

setup-protobuf:
	$(info Building protobuf files)
	cd protobuf && $(MAKE)

setup-clustering:
	$(info Building clustering)
	cd clustering && $(MAKE)

setup-embedding:
	$(info Building embedding)
	cd embedding && $(MAKE)

setup-load-balancer:
	$(info Building load-balancer)
	cd load-balancer && $(MAKE)

setup-segmentation:
	$(info Building segmentation)
	cd segmentation && $(MAKE)

setup-tracking:
	$(info Building tracking)
	cd tracking && $(MAKE)

start-clustering:
	$(info Starting clustering)
	$(MAKE) -C clustering start

start-embedding:
	$(info Starting embedding)
	$(MAKE) -C embedding start

start-load-balancer:
	$(info Starting load-balancer)
	$(MAKE) -C load-balancer start

start-segmentation:
	$(info Starting segmentation)
	$(MAKE) -C segmentation start

start-tracking:
	$(info Starting tracking)
	$(MAKE) -C tracking start

start-traefik-db:
	$(info Starting traefik and db)
	docker-compose -f docker-compose-traefik-db.yml up

start:
	$(info Starting all services)
	$(MAKE) -j6 start-clustering start-embedding start-load-balancer start-segmentation start-tracking start-traefik-db

clean:
	cd protobuf && $(MAKE) clean
	cd clustering && $(MAKE) clean
	cd embedding && $(MAKE) clean
	cd load-balancer && $(MAKE) clean
	cd segmentation && $(MAKE) clean
	cd tracking && $(MAKE) clean

.PHONY: all protobuf clustering embedding load-balancer segmentation tracking start clean