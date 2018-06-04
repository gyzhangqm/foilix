#!/usr/bin/env bash

xhost +local:foilix
docker start foilix
docker exec -it foilix /bin/bash