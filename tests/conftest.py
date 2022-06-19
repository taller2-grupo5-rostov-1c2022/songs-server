import datetime

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

from fastapi import status
import requests
import requests_mock
import pytest
from fastapi.testclient import TestClient

from src.app.subscriptions import get_time_now
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


@pytest.fixture(autouse=True)
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


@pytest.fixture(autouse=True)
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
            nested = connection.begin_nested()

    yield session

    # Rollback the overall transaction, restoring the state before the test ran.
    session.close()
    transaction.rollback()
    connection.close()


def populate_albums(test_client, albums, **kwargs):
    for album in albums:
        album_by_id = test_client.get(
            f"{API_VERSION_PREFIX}/albums/{album['id']}", **kwargs
        ).json()
        album["songs"] = album_by_id["songs"]

    return albums


def build_complete_response_for_albums(test_client, *args, **kwargs):
    response = test_client.get(*args, **kwargs)
    if response.status_code > 299:
        return response

    populated_albums = populate_albums(test_client, response.json(), **kwargs)
    resp = requests.models.Response()
    resp.status_code = response.status_code
    resp._content = json.dumps(populated_albums, indent=2).encode("utf-8")
    return resp


def populate_playlists(test_client, playlists, **kwargs):
    for playlist in playlists:
        playlist_by_id = test_client.get(
            f"{API_VERSION_PREFIX}/playlists/{playlist['id']}", **kwargs
        ).json()
        playlist["songs"] = playlist_by_id["songs"]
        playlist["colabs"] = playlist_by_id["colabs"]
    return playlists


def build_complete_response_for_playlists(test_client, *args, **kwargs):
    response = test_client.get(*args, **kwargs)
    if response.status_code > 299:
        return response

    populated_playlists = populate_playlists(test_client, response.json(), **kwargs)
    resp = requests.models.Response()
    resp.status_code = response.status_code
    resp._content = json.dumps(populated_playlists, indent=2).encode("utf-8")
    return resp


def match_wrappeable_album_endpoints(endpoint):
    if endpoint == f"{API_VERSION_PREFIX}/albums/" or endpoint.startswith(
        f"{API_VERSION_PREFIX}/albums/?"
    ):
        return True
    if endpoint == f"{API_VERSION_PREFIX}/my_albums/":
        return True
    return False


def match_wrappeable_playlist_endpoints(endpoint):
    if endpoint == f"{API_VERSION_PREFIX}/playlists/" or endpoint.startswith(
        f"{API_VERSION_PREFIX}/playlists/?"
    ):
        return True
    if endpoint == f"{API_VERSION_PREFIX}/my_playlists/":
        return True
    return False


def client_wrapper(test_client, *args, **kwargs):
    with_pagination = kwargs.pop("with_pagination", False)
    if with_pagination:
        return test_client.get(*args, **kwargs)
    else:
        endpoint = args[0]
        if match_wrappeable_album_endpoints(endpoint):
            return build_complete_response_for_albums(test_client, *args, **kwargs)
        elif match_wrappeable_playlist_endpoints(endpoint):
            return build_complete_response_for_playlists(test_client, *args, **kwargs)
        return test_client.get(*args, **kwargs)


# Workaround for expecting GET /albums/, /playlists/, /my_albums/ and /my_playlists/
# to also return the songs
class ClientPaginationWrapper:
    def __init__(self, test_client):
        self.test_client = test_client

    def __getattr__(self, item):
        if item == "get":

            def wrapper(*args, **kwargs):
                return client_wrapper(self.test_client, *args, **kwargs)

            return wrapper
        return getattr(self.test_client, item)


# For some reason, nested transactions don't work with playlists tests,
# so I need to drop the tables and create them again in that module
@pytest.fixture()
def drop_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def client(session):

    # Dependency override

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield ClientPaginationWrapper(TestClient(app))
    finally:
        del app.dependency_overrides[get_db]


@pytest.fixture()
def time_now_10_days_future():
    def get_time_now_10_days_future():
        return datetime.datetime.now() + datetime.timedelta(days=10)

    app.dependency_overrides[get_time_now] = get_time_now_10_days_future
    try:
        yield
    finally:
        del app.dependency_overrides[get_time_now]


@pytest.fixture()
def time_now_40_days_future():
    def get_time_now_40_days_future():
        return datetime.datetime.now() + datetime.timedelta(days=40)

    app.dependency_overrides[get_time_now] = get_time_now_40_days_future
