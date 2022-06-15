import datetime
from dateutil import parser

import requests_mock

from src.repositories.subscription_utils import SUBSCRIPTIONS
from tests import utils
from tests.conftest import (
    successful_payment_matcher,
    failed_payment_matcher,
    failed_wallet_creation_matcher,
)
from tests.utils import API_VERSION_PREFIX, post_user, post_user_with_sub_level


def test_get_subscriptions(client, custom_requests_mock):
    # client get subscriptions with api key

    response = client.get(
        f"{API_VERSION_PREFIX}/subscriptions/", headers={"api_key": "key"}
    )
    assert response.status_code == 200
    assert response.json() == SUBSCRIPTIONS


def test_post_user_creates_user_with_level_free_and_wallet(
    client, custom_requests_mock
):
    post_user(client, "user_id", "user_name")

    response = client.get(
        f"{API_VERSION_PREFIX}/users/user_id", headers={"api_key": "key"}
    )
    user = response.json()

    assert response.status_code == 200

    assert user["sub_level"] == 0
    assert user["sub_expires"] is None
    assert user["wallet"] == "0xA143"


def test_user_subscribes_to_premium(client, custom_requests_mock):
    custom_requests_mock.add_matcher(successful_payment_matcher)

    post_user(client, "user_id", "user_name")
    response = client.post(
        f"{API_VERSION_PREFIX}/subscriptions/",
        headers={"api_key": "key", "uid": "user_id"},
        json={"sub_level": 1},
    )

    assert response.status_code == 200

    response = client.get(
        f"{API_VERSION_PREFIX}/users/user_id", headers={"api_key": "key"}
    )
    user = response.json()

    expected_date = datetime.datetime.now() + datetime.timedelta(days=30)
    expected_date = expected_date.replace(minute=0, second=0, microsecond=0)

    assert user["sub_level"] == 1
    assert parser.parse(user["sub_expires"]) == expected_date


def test_user_subscribes_to_pro(client, custom_requests_mock):
    custom_requests_mock.add_matcher(successful_payment_matcher)

    post_user(client, "user_id", "user_name")
    response = client.post(
        f"{API_VERSION_PREFIX}/subscriptions/",
        headers={"api_key": "key", "uid": "user_id"},
        json={"sub_level": 2},
    )

    assert response.status_code == 200

    response = client.get(
        f"{API_VERSION_PREFIX}/users/user_id", headers={"api_key": "key"}
    )
    user = response.json()

    expected_date = datetime.datetime.now() + datetime.timedelta(days=30)
    expected_date = expected_date.replace(minute=0, second=0, microsecond=0)

    assert user["sub_level"] == 2
    assert parser.parse(user["sub_expires"]) == expected_date


def test_user_with_premium_returns_to_free(client, custom_requests_mock):
    post_user_with_sub_level(client, "user_id", "user_name", 1)

    response = client.post(
        f"{API_VERSION_PREFIX}/subscriptions/",
        headers={"api_key": "key", "uid": "user_id"},
        json={"sub_level": 0},
    )
    assert response.status_code == 200

    response = client.get(
        f"{API_VERSION_PREFIX}/users/user_id", headers={"api_key": "key"}
    )
    user = response.json()
    assert user["sub_level"] == 0
    assert user["sub_expires"] is None


def test_user_attempts_to_subscribe_to_premium_but_payment_fails(
    client, custom_requests_mock
):
    custom_requests_mock.add_matcher(failed_payment_matcher)

    post_user(client, "user_id", "user_name")
    response = client.post(
        f"{API_VERSION_PREFIX}/subscriptions/",
        headers={"api_key": "key", "uid": "user_id"},
        json={"sub_level": 1},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == '{"error": "Payment failed"}'

    response = client.get(
        f"{API_VERSION_PREFIX}/users/user_id", headers={"api_key": "key"}
    )

    user = response.json()
    assert user["sub_level"] == 0
    assert user["sub_expires"] is None


def test_post_user_but_wallet_creation_fails(client, custom_requests_mock):
    custom_requests_mock.add_matcher(failed_wallet_creation_matcher)

    response = post_user(client, "user_id", "user_name")

    assert response.status_code == 400
    assert response.json()["detail"] == '{"error": "Wallet creation failed"}'


def test_user_with_free_subscription_cannot_get_premium_song(
    client, custom_requests_mock
):
    post_user(client, "creator_id", "creator_name")
    post_user_with_sub_level(client, "user_id", "user_name", 0)

    song_id = utils.post_song(
        client, uid="creator_id", name="song_name", sub_level=1
    ).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"api_key": "key", "uid": "user_id"},
    )

    assert response.status_code == 403


def test_user_with_free_subscription_cannot_get_pro_song(client, custom_requests_mock):
    post_user(client, "creator_id", "creator_name")
    post_user_with_sub_level(client, "user_id", "user_name", 0)

    song_id = utils.post_song(
        client, uid="creator_id", name="song_name", sub_level=2
    ).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"api_key": "key", "uid": "user_id"},
    )

    assert response.status_code == 403


def test_user_with_premium_can_get_premium_song(client, custom_requests_mock):
    post_user(client, "creator_id", "creator_name")
    post_user_with_sub_level(client, "user_id", "user_name", 1)

    song_id = utils.post_song(
        client, uid="creator_id", name="song_name", sub_level=1
    ).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"api_key": "key", "uid": "user_id"},
    )

    assert response.status_code == 200


def test_user_with_premium_can_get_free_song(client, custom_requests_mock):
    post_user(client, "creator_id", "creator_name")
    post_user_with_sub_level(client, "user_id", "user_name", 1)

    song_id = utils.post_song(
        client, uid="creator_id", name="song_name", sub_level=0
    ).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"api_key": "key", "uid": "user_id"},
    )

    assert response.status_code == 200


def test_user_with_pro_can_get_premium_song(client, custom_requests_mock):
    post_user(client, "creator_id", "creator_name")
    response = post_user_with_sub_level(client, "user_id", "user_name", 2)
    assert response.status_code == 200

    song_id = utils.post_song(
        client, uid="creator_id", name="song_name", sub_level=1
    ).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"api_key": "key", "uid": "user_id"},
    )

    assert response.status_code == 200


def test_user_with_pro_can_get_free_song(client, custom_requests_mock):
    post_user(client, "creator_id", "creator_name")
    post_user_with_sub_level(client, "user_id", "user_name", 2)

    song_id = utils.post_song(
        client, uid="creator_id", name="song_name", sub_level=0
    ).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"api_key": "key", "uid": "user_id"},
    )

    assert response.status_code == 200
