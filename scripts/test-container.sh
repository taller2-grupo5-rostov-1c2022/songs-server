#!/bin/sh
PORT=8082 API_KEY=key docker-compose -f docker/testdb-compose.yml up --force-recreate --build --remove-orphans