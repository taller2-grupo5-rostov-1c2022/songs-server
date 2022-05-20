from tests.utils import (
    API_VERSION_PREFIX,
    post_user,
    post_song,
    post_album,
    post_playlist,
    block_song,
    post_comment,
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
    comment = response_post.json()

    assert response_post.status_code == 200
    assert comment["text"] == "this is a comment"
    assert comment["score"] == 4
    assert comment["commenter"]["name"] == "commenter_name"


def test_get_comments_with_zero_comments(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="commenter_id", user_name="commenter_name")
    album_id = post_album(client, uid="creator_id").json()["id"]

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}/comments/",
        headers={"api_key": "key", "uid": "commenter_id"},
    )
    comments = response_get.json()

    assert response_get.status_code == 200
    assert len(comments) == 0


def test_get_comments_with_one_comment(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="commenter_id", user_name="commenter_name")
    album_id = post_album(client, uid="creator_id").json()["id"]

    response_post = post_comment(
        client,
        uid="commenter_id",
        album_id=album_id,
        text="this album is awful",
        score=1,
    )

    assert response_post.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}/comments/",
        headers={"api_key": "key", "uid": "commenter_id"},
    )
    comments = response_get.json()

    assert response_get.status_code == 200
    assert len(comments) == 1
    assert comments[0]["text"] == "this album is awful"
    assert comments[0]["score"] == 1
    assert comments[0]["commenter"]["name"] == "commenter_name"


def test_get_comments_with_many_comments(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="bad_user_id", user_name="bad_commenter_name")
    post_user(client, uid="nice_user_id", user_name="nice_commenter_name")

    album_id = post_album(client, uid="creator_id").json()["id"]

    post_comment(
        client,
        uid="bad_user_id",
        album_id=album_id,
        text="this album is awful",
        score=1,
    )
    post_comment(
        client, uid="nice_user_id", album_id=album_id, text="I love this album", score=5
    )

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}/comments/",
        headers={"api_key": "key", "uid": "commenter_id"},
    )
    comments = response_get.json()

    assert response_get.status_code == 200
    assert len(comments) == 2
    assert comments[0]["text"] == "this album is awful"
    assert comments[0]["commenter"]["name"] == "bad_commenter_name"
    assert comments[1]["text"] == "I love this album"
    assert comments[1]["commenter"]["name"] == "nice_commenter_name"


def test_user_cannot_post_more_than_one_comment(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="commenter_id", user_name="commenter_name")

    album_id = post_album(client, uid="creator_id").json()["id"]

    response_post = post_comment(client, uid="commenter_id", album_id=album_id)
    assert response_post.status_code == 200

    response_post = post_comment(
        client, uid="commenter_id", album_id=album_id, text="another comment", score=2
    )
    assert response_post.status_code == 403


def test_post_comment_without_text(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="commenter_id", user_name="commenter_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    response_post = post_comment(
        client, uid="commenter_id", album_id=album_id, text=None, score=5
    )

    comment = response_post.json()
    assert response_post.status_code == 200
    assert comment["text"] is None
    assert comment["score"] == 5


def test_post_comment_without_score(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="commenter_id", user_name="commenter_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    response_post = post_comment(
        client, uid="commenter_id", album_id=album_id, text="my text", score=None
    )

    comment = response_post.json()
    assert response_post.status_code == 200
    assert comment["score"] is None
    assert comment["text"] == "my text"


def test_post_comment_without_text_or_score_should_fail(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="commenter_id", user_name="commenter_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    response_post = post_comment(
        client, uid="commenter_id", album_id=album_id, text=None, score=None
    )

    assert response_post.status_code == 422


def test_post_comment_does_not_affect_another_album(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="commenter_id", user_name="commenter_name")

    album_id_1 = post_album(client, uid="creator_id").json()["id"]
    album_id_2 = post_album(client, uid="creator_id").json()["id"]

    post_comment(client, uid="commenter_id", album_id=album_id_1, text="text", score=3)

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id_2}/comments/",
        json={"text": "updated text", "score": 5},
        headers={"api_key": "key", "uid": "commenter_id"},
    )
    comments = response_get.json()
    assert response_get.status_code == 200
    assert len(comments) == 0


def test_edit_comment_without_comment_should_fail(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="commenter_id", user_name="commenter_name")

    album_id = post_album(client, uid="creator_id").json()["id"]

    response_put = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id}/comments/",
        json={"text": "my text", "score": 4},
        headers={"api_key": "key", "uid": "commenter_id"},
    )
    print(response_put.json())
    assert response_put.status_code == 404


def test_edit_comment_in_album_with_one_comment(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="commenter_id", user_name="commenter_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    post_comment(
        client, uid="commenter_id", album_id=album_id, text="original text", score=2
    )

    response_put = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id}/comments/",
        json={"text": "updated text", "score": 5},
        headers={"api_key": "key", "uid": "commenter_id"},
    )
    assert response_put.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}/comments/",
        headers={"api_key": "key", "uid": "commenter_id"},
    )
    comments = response_get.json()
    assert response_get.status_code == 200
    assert len(comments) == 1
    assert comments[0]["text"] == "updated text"
    assert comments[0]["score"] == 5


def test_edit_comment_in_album_with_many_comments(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="first_commenter_id", user_name="first_commenter_name")
    post_user(client, uid="second_commenter_id", user_name="second_commenter_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    post_comment(
        client, uid="first_commenter_id", album_id=album_id, text="awful album", score=2
    )
    post_comment(
        client, uid="second_commenter_id", album_id=album_id, text="text", score=2
    )

    new_text = "I changed my mind, this album is awesome"

    response_put = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id}/comments/",
        json={"text": new_text, "score": 5},
        headers={"api_key": "key", "uid": "first_commenter_id"},
    )
    assert response_put.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}/my_comment/",
        headers={"api_key": "key", "uid": "first_commenter_id"},
    )
    comment = response_get.json()
    assert response_get.status_code == 200
    assert comment["text"] == new_text
    assert comment["score"] == 5


def test_cannot_edit_comment_of_another_user(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="first_commenter_id", user_name="first_commenter_name")
    post_user(client, uid="second_commenter_id", user_name="second_commenter_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    post_comment(
        client,
        uid="first_commenter_id",
        album_id=album_id,
        text="original text",
        score=2,
    )

    response_put = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id}/comments/",
        json={"text": "I'm trying to change a comment", "score": 3},
        headers={"api_key": "key", "uid": "second_commenter_id"},
    )
    assert response_put.status_code == 404

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}/my_comment/",
        headers={"api_key": "key", "uid": "first_commenter_id"},
    )
    comment = response_get.json()
    assert response_get.status_code == 200
    assert comment["text"] == "original text"
    assert comment["score"] == 2


def test_delete_comment_in_album_with_zero_comments_should_fail(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="commenter_id", user_name="commenter_name")

    album_id = post_album(client, uid="creator_id").json()["id"]

    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/albums/{album_id}/comments/",
        headers={"api_key": "key", "uid": "commenter_id"},
    )
    assert response_delete.status_code == 404


def test_delete_comment_in_album_with_comment(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="commenter_id", user_name="commenter_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    post_comment(
        client, uid="commenter_id", album_id=album_id, text="original text", score=2
    )

    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/albums/{album_id}/comments/",
        headers={"api_key": "key", "uid": "commenter_id"},
    )
    assert response_delete.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}/comments/",
        headers={"api_key": "key", "uid": "commenter_id"},
    )
    comments = response_get.json()
    assert response_get.status_code == 200
    assert len(comments) == 0


def test_post_comment_in_album_with_blocked_songs_should_not_remove_songs(client):
    # This is a white box test

    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="commenter_id", user_name="commenter_name")

    song_id = post_song(client, uid="creator_id", name="happy_song").json()["id"]
    album_id = post_album(client, uid="creator_id", songs_ids=[song_id]).json()["id"]

    block_song(client, song_id)

    response_post = post_comment(
        client, uid="commenter_id", album_id=album_id, text="my text", score=3
    )
    assert response_post.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"api_key": "key", "uid": "song_creator_id", "role": "admin"},
    )
    assert response_get.status_code == 200


def test_post_one_comment_affects_album_score(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="commenter_id", user_name="commenter_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    post_comment(client, "commenter_id", album_id, "bad song", 2)

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"api_key": "key", "uid": "song_creator_id", "role": "admin"},
    )
    album = response_get.json()
    assert response_get.status_code == 200
    assert album["score"] == 2


def test_post_many_comments_affects_score(client):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="first_commenter_id", user_name="first_commenter_name")
    post_user(client, uid="second_commenter_id", user_name="second_commenter_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    post_comment(client, "first_commenter_id", album_id, "bad song", 2)
    post_comment(client, "second_commenter_id", album_id, "good song", 5)

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"api_key": "key", "uid": "song_creator_id", "role": "admin"},
    )
    album = response_get.json()
    assert response_get.status_code == 200
    assert album["score"] == 3.5
