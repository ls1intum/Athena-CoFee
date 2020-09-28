#!/bin/bash

COMPONENT=$1      # Parameter $1 (Component): either "segmentation", "embedding", "tracking", or "clustering"

echo -e "INFO: Building ${COMPONENT}-component"

REGISTRY=docker.pkg.github.com                          # Address of Docker Registry
IMAGE=${REGISTRY}/ls1intum/athene/athene-${COMPONENT}   # Name of the Docker image
TAG=$(git rev-parse --short "$GITHUB_SHA")              # Tag image with short commit hash by default

# Build and Push image
echo -e "INFO: Build and Push ${IMAGE}:${TAG}"
cd ${COMPONENT}; docker build . --file Dockerfile --tag ${IMAGE}:${TAG}
docker push ${IMAGE}:${TAG}

# Tag and Push with branch-name
echo "INFO: Branch-tag and Push image additionally as ${IMAGE}:${GITHUB_REF##*/}"
docker tag ${IMAGE}:${TAG} ${IMAGE}:${GITHUB_REF##*/}
docker push ${IMAGE}:${GITHUB_REF##*/}

# Tag and Push as latest if building on master-branch
if [ "${GITHUB_REF##*/}" = "master" ]; then
  echo "INFO: Tag and Push image additionally as ${IMAGE}:latest"
  docker tag ${IMAGE}:${TAG} ${IMAGE}:latest
  docker push ${IMAGE}:latest
  docker tag ${IMAGE}:${TAG} ls1intum/athene-${COMPONENT}
  docker push ls1intum/athene-${COMPONENT}
fi
