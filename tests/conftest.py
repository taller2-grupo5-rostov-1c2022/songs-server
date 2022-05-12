import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.postgres.database import get_db, Base

import os

SQLALCHEMY_DATABASE_URL = os.environ.get("TEST_POSTGRES_URL")


@pytest.fixture(scope="session")
def connect_to_database():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    for x in range(10):
        try:
            print("Trying to connect to DB - " + str(x))
            engine.connect()
            break
        except Exception:  # noqa: E722 # Want to catch all exceptions
            time.sleep(1)
            engine = create_engine(SQLALCHEMY_DATABASE_URL)
    yield engine


@pytest.fixture()
def session(connect_to_database):

    Base.metadata.drop_all(bind=connect_to_database)
    Base.metadata.create_all(bind=connect_to_database)
    testing_session_local = sessionmaker(
        autocommit=False, autoflush=False, bind=connect_to_database
    )

    db = testing_session_local()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):

    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)
