#!/usr/bin/env bash

xhost +local:foilix-py3
docker start foilix-py3
docker exec -it foilix-py3 /bin/bash