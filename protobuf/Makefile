all: python_client

python_client: clustering.proto
	protoc --version || (echo "Please install protoc: https://grpc.io/docs/protoc-installation/"; exit 1)
	protoc --python_out ../load-balancer/src/ clustering.proto

clean:
	rm -f ../load-balancer/src/clustering_pb2.py