#!/bin/sh
PORT=8082 API_KEY=key docker-compose -f docker/coverage-compose.yml up --force-recreate --build --remove-orphans --abort-on-container-exit