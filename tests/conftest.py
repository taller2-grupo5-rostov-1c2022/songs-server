import time
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker, declarative_base

from fastapi import status
import requests
import requests_mock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from src.main import app, API_VERSION_PREFIX
from src.database.access import get_db, Base
from src.utils.subscription import CREATE_WALLET_ENDPOINT, DEPOSIT_ENDPOINT
import json

import os

SQLALCHEMY_DATABASE_URL = os.environ.get("TEST_POSTGRES_URL")
engine = sa.create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(engine)
Base.metadata.create_all(bind=engine)

SUCCESSFUL_PAYMENT_RESPONSE = {
    "nonce": 2,
    "gasPrice": {"type": "BigNumber", "hex": "0x4190ab08"},
    "gasLimit": {"type": "BigNumber", "hex": "0x6d78"},
    "to": "0xE9f7F026355d691238F628Cd8BCBb39Bf7F4f8E2",
    "value": {"type": "BigNumber", "hex": "0x5af3107a4000"},
    "data": "0xd0e30db0",
    "chainId": 4,
    "v": 43,
    "r": "0xc8fc145f611e8e5552374c3dedc2f588458d7214a523b095d70f5478bf06bdf8",
    "s": "0x0ff83c7c81028bfa59aa8375b489daaa77787aa80ba4d7421a1ea09621abc607",
    "from": "0xaa994f63f812A136158aC937aCC806E40b85739d",
    "hash": "0xcc9c8acb976d44bc96e4a10f6c89d7431ab5e08fc681db5a6e682c213ab5c101",
}


def successful_payment_matcher(request):
    if request.url.startswith(DEPOSIT_ENDPOINT):
        resp = requests.models.Response()
        resp.status_code = status.HTTP_200_OK
        resp._content = json.dumps(SUCCESSFUL_PAYMENT_RESPONSE, indent=2).encode(
            "utf-8"
        )
        return resp
    return None


def failed_payment_matcher(request):
    if request.url.startswith(DEPOSIT_ENDPOINT):
        resp = requests.models.Response()
        resp.status_code = status.HTTP_400_BAD_REQUEST
        resp._content = b'{"error": "Payment failed"}'
        return resp
    return None


def successful_wallet_creation_matcher(request):
    if request.url.startswith(CREATE_WALLET_ENDPOINT) and request.method == "POST":
        resp = requests.models.Response()
        resp.status_code = status.HTTP_200_OK
        resp._content = (
            b'{"address": "0xA143", "id": "user_id", "private_key": "11111"}'
        )
        return resp
    return None


def failed_wallet_creation_matcher(request):
    if request.url.startswith(CREATE_WALLET_ENDPOINT) and request.method == "POST":
        resp = requests.models.Response()
        resp.status_code = status.HTTP_400_BAD_REQUEST
        resp._content = b'{"error": "Wallet creation failed"}'
        return resp
    return None


def api_matcher(request):
    if API_VERSION_PREFIX not in request.url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attepmted to call non-api endpoint",
        )
    return None


@pytest.fixture
def custom_requests_mock():
    m = requests_mock.Mocker(real_http=True)
    m.start()
    m.add_matcher(api_matcher)
    m.add_matcher(successful_wallet_creation_matcher)
    m.add_matcher(successful_payment_matcher)

    try:
        yield m
    finally:
        m.stop()


@pytest.fixture()
def session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Begin a nested transaction (using SAVEPOINT).
    nested = connection.begin_nested()

    # If the application code calls session.commit, it will end the nested
    # transaction. Need to start a new one when that happens.
    @sa.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            print("Starting a new savepoint")
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        # Rollback the overall transaction, restoring the state before the test ran.
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(session):

    # Dependency override

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        del app.dependency_overrides[get_db]
