[![Pipeline](https://github.com/taller2-grupo5-rostov-1c2022/songs-server/actions/workflows/pipeline.yml/badge.svg?branch=master)](https://github.com/taller2-grupo5-rostov-1c2022/songs-server/actions/workflows/pipeline.yml)
[![codecov](https://codecov.io/gh/taller2-grupo5-rostov-1c2022/songs-server/branch/master/graph/badge.svg?token=LJIu1T1HQr)](https://codecov.io/gh/taller2-grupo5-rostov-1c2022/songs-server)
[![](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/)
[![](https://img.shields.io/badge/docs-fastapi-blue.svg)](https://fastapi.tiangolo.com/)
![](https://img.shields.io/badge/version-0.1-blue.svg)

# Spotifiuby Songs Server

## Installing the project

The only dependency required to use this template is [poetry](https://python-poetry.org). The recommended method to install it is through [pip](https://pypi.org/project/pip/).

```bash
$ pip3 install poetry
$ poetry config virtualenvs.in-project true
```

Remember to commit to the repo the `poetry.lock` file generated by `poetry install`.

### Initiating the venv

```
$ poetry shell
```

## Dependencies

The virtual environment is automatically created and activated via poetry.

```
$ cd to-project-path
$ poetry install
```

To make sure everything is set up correctly, run the following command which must show the virtual environment path:

```
$ poetry show -v
```

### Adding new dependencies

Check the [full poetry docs](https://python-poetry.org/docs/cli/), but here goes a quick reminder,

```bash
poetry add <dependency> [--dev]
```

### Style guide

This template follows [PEP8](https://www.python.org/dev/peps/pep-0008/).

For this purpose, we use:

- [black](https://github.com/psf/black): an opinionated code formatting tool
- [flake8](https://github.com/PyCQA/flake8): a tool to enforce style guide
- [pylint](https://github.com/PyCQA/pylint): a source code, bug and quality checker

**Linters**

```bash
flake8 && pylint <module_name>
```

```bash
flake8 . && pylint src
```

**Formatter**

```bash
black .
```

## Running the server

- Development: `uvicorn src.main:app --reload`
- Production: `uvicorn src.main:app`
- Container: `PORT=8082 docker-compose up`
- Rebuilt Container: `PORT=8082 docker-compose up --force-recreate --build`

## API Documentation

Documentation will be automatically generated at `{app}/docs`

## Tests

We use the [pytest framework](https://fastapi.tiangolo.com/tutorial/testing/) to test. The easiest way to run tests is `pytest`.
Remember to create functions with a name that starts with `test_` (this is standard pytest conventions).

## Github Actions

A few pipelines have been set to run on github actions to ensure code quality and deployment.

- Run Linter
- Run Tests
- Upload Test Coverage
- Deploy to Heroku using docker image

### Upload Coverage to Codecov

The pipeline automatically generates a coverage report and uploads it to [codecov](https://about.codecov.io/)

You'll need to set the following actions secrets:

- `CODECOV_TOKEN`: Repo Token. Can be obtained on codecov when setting up or on settings

## Heroku

You'll need to set the following actions secrets:

- `HEROKU_APP_NAME`: App name
- `HEROKU_EMAIL`: Account email
- `HEROKU_API_KEY`: Account [API key](https://dashboard.heroku.com/account)
- `API_KEY`: This app's api-key, needed to make requests

## Datadog

The heroku Dockerfile includes the DataDog agent. Create a new DataDog API Key from [here](https://app.datadoghq.com/organization-settings/api-keys).
Also, you need to set the following config vars in Heroku (you can use [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) if you want):

```bash
DD_API_KEY=<api_key_from_datadog>
DD_DYNO_HOST=false
HEROKU_APP_NAME=<app_name>
DD_TAGS=service:<meaningful_tag_for_datadog>
```

## Firebase

To access the database and storage, you'll need to generate a Firebase private key.

To do so, go to **Project configuration** > **Service accounts** > **Generate new private key**. [[Link](https://console.firebase.google.com/u/0/project/rostov-spotifiuby/settings/serviceaccounts/adminsdk)]

Save the file as `google-credentials.json` in the root directory of the repository.

You can also set `TESTING=1` as an environment variable to use mocks of the database
and storage for testing purposes.

In order to load the credentials in Heroku, set `GOOGLE_CREDENTIALS` as an environment variable in Heroku, and paste the content of the `google-credentials.json` file.
## Postgres

You'll need to set `POSTGRES_URL` as an environment variable (locally or on heroku) or `HD_POSTGRES_URL` as an action secret

Useful links:
- [postgresql](https://www.postgresql.org/)
- [pgadmin](https://www.pgadmin.org/)

### Credentials

- Go to: Songs Server > Resources > Heroku Postgres > Settings [[Link](https://data.heroku.com/datastores/3666c9aa-cd88-4790-84e2-545a4857f0b0#administration)]
- View Credentials

### pgAdmin

#### Set Up

- Add New Server
- When registering , copy the following from Heroku Postgres Credentials ([Tut](https://www.youtube.com/watch?v=MLow0gI6oNY&ab_channel=SinRuedaTecnol%C3%B3gica))
  - Connection > Host Name <- Host
  - Connection > Maintenance Database <- Database
  - Advanced > DB Restrictions <- Database
  - Connection > Username <- User
  - Connection > Password <- Password

#### SQL

- [Tutorial](https://www.w3schools.com/sql/default.asp)

### Environment Variables

```
POSTGRES_URL="postgresql://{username}:{password}@{host}:{port}/{database}"
```

### Links

- https://dev.to/andre347/how-to-easily-create-a-postgres-database-in-docker-4moj
- https://levelup.gitconnected.com/creating-and-filling-a-postgres-db-with-docker-compose-e1607f6f882f

#### Development

##### Running Test Container and database

```
sudo ./scripts/test-container.sh
```

server needs to be stopped and rebuilt when making changes, the database persists.

##### Altering database schema

- edit
  - `docker/sql/create_tables.sql`
  - `src/postgres/models.py`
- delete `docker/postgres-data`

##### Running test

```
sudo ./scripts/coverage-container.sh
```

you can also run a test-container and run the tests from the cli
