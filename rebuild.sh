#!/usr/bin/env bash

docker build -t emu-server-python -f Dockerfile.ws .
docker build -t emu-server-ngnix -f Dockerfile.nginx .
