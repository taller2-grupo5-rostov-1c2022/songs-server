from tests.utils import API_VERSION_PREFIX, post_user, post_streaming


def test_artist_post_streaming(client):
    post_user(client, "streaming_user_id", "streaming_user_name")

    response_post = client.post(
        f"{API_VERSION_PREFIX}/streamings/",
        headers={"api_key": "key", "uid": "streaming_user_id", "role": "artist"},
    )
    assert response_post.status_code == 200


def test_post_streaming_with_invalid_uid_should_fail(client):

    response_post = client.post(
        f"{API_VERSION_PREFIX}/streamings/",
        headers={"api_key": "key", "uid": "invalid_uid"},
    )
    assert response_post.status_code == 404


def test_listener_post_streaming_should_fail(client):
    post_user(client, "listener_user_id", "listener_user_name")

    response_post = client.post(
        f"{API_VERSION_PREFIX}/streamings/",
        headers={"api_key": "key", "uid": "listener_user_id", "role": "listener"},
    )
    assert response_post.status_code == 403


def test_user_post_streaming_twice_should_fail(client):
    post_user(client, "streaming_user_id", "streaming_user_name")

    response_post = client.post(
        f"{API_VERSION_PREFIX}/streamings/",
        headers={"api_key": "key", "uid": "streaming_user_id", "role": "artist"},
    )
    assert response_post.status_code == 200

    response_post = client.post(
        f"{API_VERSION_PREFIX}/streamings/",
        headers={"api_key": "key", "uid": "streaming_user_id", "role": "artist"},
    )
    assert response_post.status_code == 403


def test_get_streamings_without_streamings(client):
    post_user(client, "streaming_user_id", "streaming_user_name")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/streamings/",
        headers={"api_key": "key", "uid": "streaming_user_id"},
    )
    streamings = response_get.json()

    assert response_get.status_code == 200
    assert len(streamings) == 0


def test_get_streamings_with_one_streaming(client):
    post_user(client, "streaming_user_id", "streaming_user_name")
    post_user(client, "listener_user_id", "listener_user_name")

    response_post = client.post(
        f"{API_VERSION_PREFIX}/streamings/",
        headers={"api_key": "key", "uid": "streaming_user_id", "role": "artist"},
    )
    assert response_post.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/streamings/",
        headers={"api_key": "key", "uid": "listener_user_id"},
    )

    assert response_post.status_code == 200
    streamings = response_get.json()

    assert response_get.status_code == 200
    assert len(streamings) == 1
    assert streamings[0]["id"] == "streaming_user_id"
    assert streamings[0]["name"] == "streaming_user_name"
    assert streamings[0]["token"] is not None


def test_get_streamings_with_two_streamings(client):
    post_user(client, "streaming_user_id", "streaming_user_name")
    post_user(client, "streaming_user_id_2", "streaming_user_name_2")

    response_post = post_streaming(client, "streaming_user_id")
    assert response_post.status_code == 200

    response_post = post_streaming(client, "streaming_user_id_2")
    assert response_post.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/streamings/",
        headers={"api_key": "key", "uid": "streaming_user_id"},
    )
    streamings = response_get.json()

    assert response_get.status_code == 200
    assert len(streamings) == 2


def test_delete_streaming_deletes_it(client):
    post_user(client, "streaming_user_id", "streaming_user_name")

    response_post = post_streaming(client, "streaming_user_id")
    assert response_post.status_code == 200

    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/streamings/",
        headers={"api_key": "key", "uid": "streaming_user_id"},
    )
    assert response_delete.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/streamings/",
        headers={"api_key": "key", "uid": "streaming_user_id"},
    )
    streamings = response_get.json()

    assert response_get.status_code == 200
    assert len(streamings) == 0


def test_delete_streaming_with_invalid_uid_should_fail(client):
    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/streamings/",
        headers={"api_key": "key", "uid": "invalid_uid"},
    )
    assert response_delete.status_code == 404


def test_token_for_streamer_is_not_the_same_as_token_for_listener(client):
    post_user(client, "streaming_user_id", "streaming_user_name")
    post_user(client, "listener_user_id", "listener_user_name")

    response_post = post_streaming(client, "streaming_user_id")
    token_streamer = response_post.json()

    response_get = client.get(
        f"{API_VERSION_PREFIX}/streamings/",
        headers={"api_key": "key", "uid": "listener_user_id"},
    )
    streamings = response_get.json()

    assert response_get.status_code == 200
    assert len(streamings) == 1
    assert streamings[0]["token"] != token_streamer