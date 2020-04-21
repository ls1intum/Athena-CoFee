#!/bin/bash

# Parameter $1 (Component): either "segmentation" or "clustering"
COMPONENT=$1

# Address of Docker Registry
REGISTRY=docker.pkg.github.com
# Name of the Docker image
IMAGE=${REGISTRY}/ls1intum/athene/athene-${COMPONENT}
# Tag image with short commit hash by default
TAG=$(git rev-parse --short "$GITHUB_SHA")

# Build and Push image
cd ${COMPONENT}; docker build . --file Dockerfile --tag ${IMAGE}:${TAG}
docker push ${IMAGE}:${TAG}

# Tag and Push as branch-name
docker tag ${IMAGE}:${TAG} ${IMAGE}:${GITHUB_REF##*/}
echo "Image additionally branch-tagged as ${IMAGE}:${GITHUB_REF##*/}"
docker push ${IMAGE}:${GITHUB_REF##*/}

# Tag and Push as latest if on master-branch
if [ "${GITHUB_REF##*/}" = "master" ]; then
  docker tag ${IMAGE}:${TAG} ${IMAGE}:latest
  echo "Image additionally tagged as ${IMAGE}:latest"
  docker push ${IMAGE}:latest
fi