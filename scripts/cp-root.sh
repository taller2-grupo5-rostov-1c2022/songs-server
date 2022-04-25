#!/bin/sh

# Hay que copiar el heroku-Dockerfile a root por un tema de la Action del deploy de Heroku. No deja referenciar algun Dockerfile en particular.
eval cp docker/heroku-Dockerfile .
eval mv heroku-Dockerfile Dockerfile
eval cp scripts/add-google-credentials.sh .
eval cp scripts/heroku-entrypoint.sh .

eval cp docker/cov/coverage.xml .