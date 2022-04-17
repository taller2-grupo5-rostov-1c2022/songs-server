#!/bin/sh

echo "Generating google-credentials.json from Heroku environment variable"

echo $GOOGLE_CREDENTIALS > google-credentials.json

exec "$@"