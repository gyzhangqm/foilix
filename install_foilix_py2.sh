#!/usr/bin/env bash

home="${1:-$HOME}"

imageName="guillaume-florent/foilix-py2:latest"
containerName="foilix-py2"
displayVar="$DISPLAY"

docker build --file Dockerfile.py2 --tag ${imageName} .

docker run  -it -d --name ${containerName}                  \
    -e DISPLAY=${displayVar}                                \
    --workdir="${home}"                                     \
    --volume="${home}:${home}"                              \
     -v=/tmp/.X11-unix:/tmp/.X11-unix ${imageName}          \
     /bin/bash