#!/bin/sh

PORT=8082 API_KEY=key docker-compose -f docker/docker-compose.yml up --force-recreate --build