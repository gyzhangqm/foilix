#!/usr/bin/env bash

xhost +local:foilix-py2
docker start foilix-py2
docker exec -it foilix-py2 /bin/bash