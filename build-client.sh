cd protobuf || exit
protoc --java_out ../client/src/main/java/ clustering.proto # you need to have protobuf installed
cd ..