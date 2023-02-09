cd protobuf || exit
protoc --python_out ../load-balancer/src/ clustering.proto # you need to have protobuf installed
cd ..