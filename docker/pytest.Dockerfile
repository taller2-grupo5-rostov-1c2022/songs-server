FROM python:3.9

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=off PIP_DISABLE_PIP_VERSION_CHECK=on POETRY_NO_INTERACTION=1

# install poetry
RUN pip install poetry

# copy project requirement files here to ensure they will be cached.
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

COPY ./google-credentials.json ./google-credentials.json
# ENTRYPOINT ["sh", "/app/add-google-credentials.sh"]

# install runtime deps
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

COPY ./src ./src/
COPY ./tests ./tests/
COPY ./scripts/docker-entrypoint.sh ./docker-entrypoint.sh

RUN chmod +x ./docker-entrypoint.sh

RUN sleep 5

RUN mkdir cov

RUN poetry run pytest --cov=./ --cov-report=xml

RUN mv coverage.xml cov/coverage.xml

CMD ["./docker-entrypoint.sh"]