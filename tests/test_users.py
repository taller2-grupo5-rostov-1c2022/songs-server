from tests.utils import API_VERSION_PREFIX, post_user


def test_unauthorized_get(client):
    response = client.get(f"{API_VERSION_PREFIX}/users/")
    assert response.status_code == 403


def test_get_users(client):
    response = client.get(f"{API_VERSION_PREFIX}/users/",
                          headers={"api_key": "key"})
    assert response.status_code == 200


def test_post_user(client):
    response_post = post_user(client, "new_user_id", "user_name")
    assert response_post.status_code == 200

    response_get = client.get(f"{API_VERSION_PREFIX}/users/new_user_id",
                              headers={"api_key"})