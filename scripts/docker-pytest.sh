#!/bin/sh

echo WAIT FOR SERVICE
echo RUN TESTS
poetry run pytest --cov=./ --cov-report=xml --no-cov-on-fail
mv coverage.xml cov/coverage.xml