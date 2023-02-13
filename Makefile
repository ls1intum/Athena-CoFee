all: protobuf clustering embedding load-balancer segmentation tracking

protobuf:
	$(info Building protobuf files)
	cd protobuf && $(MAKE)

clustering:
	$(info Building clustering)
	cd clustering && $(MAKE)

embedding:
	$(info Building embedding)
	cd embedding && $(MAKE)

load-balancer:
	$(info Building load-balancer)
	cd load-balancer && $(MAKE)

segmentation:
	$(info Building segmentation)
	cd segmentation && $(MAKE)

tracking:
	$(info Building tracking)
	cd tracking && $(MAKE)

clean:
	cd protobuf && $(MAKE) clean
	cd clustering && $(MAKE) clean
	cd embedding && $(MAKE) clean
	cd load-balancer && $(MAKE) clean
	cd segmentation && $(MAKE) clean
	cd tracking && $(MAKE) clean

.PHONY: all protobuf clustering embedding load-balancer segmentation tracking clean