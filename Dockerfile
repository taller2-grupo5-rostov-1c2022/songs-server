FROM python:3.9

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=off PIP_DISABLE_PIP_VERSION_CHECK=on OETRY_NO_INTERACTION=1

# install poetry
RUN pip install poetry

# copy project requirement files here to ensure they will be cached.
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# install runtime deps
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

COPY ./src ./src/
COPY ./docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x ./docker-entrypoint.sh

CMD ["./docker-entrypoint.sh"]