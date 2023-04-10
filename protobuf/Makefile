all: java_client python_client

java_client: clustering.proto
	protoc --version || (echo "Please install protoc: https://grpc.io/docs/protoc-installation/"; exit 1)
	protoc --java_out ../client/src/main/java/ clustering.proto

python_client: clustering.proto
	protoc --version || (echo "Please install protoc: https://grpc.io/docs/protoc-installation/"; exit 1)
	protoc --python_out ../load-balancer/src/ clustering.proto

clean:
	rm -rf ../client/src/main/java/de/tum/in/ase/athene/protobuf/*.java
	rm -f ../load-balancer/src/clustering_pb2.py