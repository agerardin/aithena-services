#!/bin/bash

version=$(<docker/VERSION)
# docker buildx build --platform linux/amd64 -t aithena-services:${version} -f docker/Dockerfile .
docker buildx build --platform linux/amd64,linux/arm64 -t agerardin/aithena-services:${version} -f docker/Dockerfile --push .
# docker build -t aithena-services:${version} -f docker/Dockerfile .