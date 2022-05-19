from tests.utils import (
    API_VERSION_PREFIX,
    post_user,
    post_song,
    post_album,
    post_playlist,
    block_song,
)


def test_post_comment(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="commenter_id", user_name="commenter_name")
    album_id = post_album(client, uid="creator_id").json()["id"]

    response_post = client.post(
        f"{API_VERSION_PREFIX}/albums/{album_id}/comments/",
        json={"text": "this is a comment", "score": 4},
        headers={"api_key": "key", "uid": "commenter_id"},
    )
    assert response_post.status_code == 200
