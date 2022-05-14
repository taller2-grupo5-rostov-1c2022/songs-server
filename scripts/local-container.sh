#!/bin/sh

PORT=8082 API_KEY=key docker-compose  --env-file .env -f docker/docker-compose.yml up --force-recreate --build