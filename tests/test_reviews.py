from tests.utils import (
    API_VERSION_PREFIX,
    post_user,
    post_song,
    post_album,
    post_playlist,
    block_song,
    post_review,
)


def test_post_review(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="reviewer_id", user_name="reviewer_name")
    album_id = post_album(client, uid="creator_id").json()["id"]

    response_post = client.post(
        f"{API_VERSION_PREFIX}/albums/{album_id}/reviews/",
        json={"text": "this is a review", "score": 4},
        headers={"api_key": "key", "uid": "reviewer_id"},
    )
    review = response_post.json()

    assert response_post.status_code == 200
    assert review["text"] == "this is a review"
    assert review["score"] == 4
    assert review["reviewer"]["name"] == "reviewer_name"


def test_get_reviews_with_zero_reviews(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="reviewer_id", user_name="reviewer_name")
    album_id = post_album(client, uid="creator_id").json()["id"]

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}/reviews/",
        headers={"api_key": "key", "uid": "reviewer_id"},
    )
    reviews = response_get.json()

    assert response_get.status_code == 200
    assert len(reviews) == 0


def test_get_reviews_with_one_review(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="reviewer_id", user_name="reviewer_name")
    album_id = post_album(client, uid="creator_id").json()["id"]

    response_post = post_review(
        client,
        uid="reviewer_id",
        album_id=album_id,
        text="this album is awful",
        score=1,
    )

    assert response_post.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}/reviews/",
        headers={"api_key": "key", "uid": "reviewer_id"},
    )
    reviews = response_get.json()

    assert response_get.status_code == 200
    assert len(reviews) == 1
    assert reviews[0]["text"] == "this album is awful"
    assert reviews[0]["score"] == 1
    assert reviews[0]["reviewer"]["name"] == "reviewer_name"


def test_get_reviews_with_many_reviews(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="bad_user_id", user_name="bad_reviewer_name")
    post_user(client, uid="nice_user_id", user_name="nice_reviewer_name")

    album_id = post_album(client, uid="creator_id").json()["id"]

    post_review(
        client,
        uid="bad_user_id",
        album_id=album_id,
        text="this album is awful",
        score=1,
    )
    post_review(
        client, uid="nice_user_id", album_id=album_id, text="I love this album", score=5
    )

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}/reviews/",
        headers={"api_key": "key", "uid": "reviewer_id"},
    )
    reviews = response_get.json()

    assert response_get.status_code == 200
    assert len(reviews) == 2
    assert reviews[0]["text"] == "this album is awful"
    assert reviews[0]["reviewer"]["name"] == "bad_reviewer_name"
    assert reviews[1]["text"] == "I love this album"
    assert reviews[1]["reviewer"]["name"] == "nice_reviewer_name"


def test_user_cannot_post_more_than_one_review(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="reviewer_id", user_name="reviewer_name")

    album_id = post_album(client, uid="creator_id").json()["id"]

    response_post = post_review(client, uid="reviewer_id", album_id=album_id)
    assert response_post.status_code == 200

    response_post = post_review(
        client, uid="reviewer_id", album_id=album_id, text="another review", score=2
    )
    assert response_post.status_code == 403


def test_post_review_without_text(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="reviewer_id", user_name="reviewer_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    response_post = post_review(
        client, uid="reviewer_id", album_id=album_id, text=None, score=5
    )

    review = response_post.json()
    assert response_post.status_code == 200
    assert review["text"] is None
    assert review["score"] == 5


def test_post_review_without_score(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="reviewer_id", user_name="reviewer_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    response_post = post_review(
        client, uid="reviewer_id", album_id=album_id, text="my text", score=None
    )

    review = response_post.json()
    assert response_post.status_code == 200
    assert review["score"] is None
    assert review["text"] == "my text"


def test_post_review_without_text_or_score_should_fail(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="reviewer_id", user_name="reviewer_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    response_post = post_review(
        client, uid="reviewer_id", album_id=album_id, text=None, score=None
    )

    assert response_post.status_code == 422


def test_post_review_does_not_affect_another_album(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="reviewer_id", user_name="reviewer_name")

    album_id_1 = post_album(client, uid="creator_id").json()["id"]
    album_id_2 = post_album(client, uid="creator_id").json()["id"]

    post_review(client, uid="reviewer_id", album_id=album_id_1, text="text", score=3)

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id_2}/reviews/",
        json={"text": "updated text", "score": 5},
        headers={"api_key": "key", "uid": "reviewer_id"},
    )
    reviews = response_get.json()
    assert response_get.status_code == 200
    assert len(reviews) == 0


def test_edit_review_without_review_should_fail(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="reviewer_id", user_name="reviewer_name")

    album_id = post_album(client, uid="creator_id").json()["id"]

    response_put = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id}/reviews/",
        json={"text": "my text", "score": 4},
        headers={"api_key": "key", "uid": "reviewer_id"},
    )
    assert response_put.status_code == 404


def test_edit_review_in_album_with_one_review(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="reviewer_id", user_name="reviewer_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    post_review(
        client, uid="reviewer_id", album_id=album_id, text="original text", score=2
    )

    response_put = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id}/reviews/",
        json={"text": "updated text", "score": 5},
        headers={"api_key": "key", "uid": "reviewer_id"},
    )
    assert response_put.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}/reviews/",
        headers={"api_key": "key", "uid": "reviewer_id"},
    )
    reviews = response_get.json()
    assert response_get.status_code == 200
    assert len(reviews) == 1
    assert reviews[0]["text"] == "updated text"
    assert reviews[0]["score"] == 5


def test_edit_review_in_album_with_many_reviews(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="first_reviewer_id", user_name="first_reviewer_name")
    post_user(client, uid="second_reviewer_id", user_name="second_reviewer_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    post_review(
        client, uid="first_reviewer_id", album_id=album_id, text="awful album", score=2
    )
    post_review(
        client, uid="second_reviewer_id", album_id=album_id, text="text", score=2
    )

    new_text = "I changed my mind, this album is awesome"

    response_put = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id}/reviews/",
        json={"text": new_text, "score": 5},
        headers={"api_key": "key", "uid": "first_reviewer_id"},
    )
    assert response_put.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}/my_review/",
        headers={"api_key": "key", "uid": "first_reviewer_id"},
    )
    review = response_get.json()
    assert response_get.status_code == 200
    assert review["text"] == new_text
    assert review["score"] == 5


def test_cannot_edit_review_of_another_user(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="first_reviewer_id", user_name="first_reviewer_name")
    post_user(client, uid="second_reviewer_id", user_name="second_reviewer_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    post_review(
        client,
        uid="first_reviewer_id",
        album_id=album_id,
        text="original text",
        score=2,
    )

    response_put = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id}/reviews/",
        json={"text": "I'm trying to change a review", "score": 3},
        headers={"api_key": "key", "uid": "second_reviewer_id"},
    )
    assert response_put.status_code == 404

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}/my_review/",
        headers={"api_key": "key", "uid": "first_reviewer_id"},
    )
    review = response_get.json()
    assert response_get.status_code == 200
    assert review["text"] == "original text"
    assert review["score"] == 2


def test_delete_review_in_album_with_zero_reviews_should_fail(
    client, custom_requests_mock
):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="reviewer_id", user_name="reviewer_name")

    album_id = post_album(client, uid="creator_id").json()["id"]

    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/albums/{album_id}/reviews/",
        headers={"api_key": "key", "uid": "reviewer_id"},
    )
    assert response_delete.status_code == 404


def test_delete_review_in_album_with_review(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="reviewer_id", user_name="reviewer_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    post_review(
        client, uid="reviewer_id", album_id=album_id, text="original text", score=2
    )

    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/albums/{album_id}/reviews/",
        headers={"api_key": "key", "uid": "reviewer_id"},
    )
    assert response_delete.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}/reviews/",
        headers={"api_key": "key", "uid": "reviewer_id"},
    )
    reviews = response_get.json()
    assert response_get.status_code == 200
    assert len(reviews) == 0


def test_post_review_in_album_with_blocked_songs_should_not_remove_songs(
    client, custom_requests_mock
):
    # This is a white box test

    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="reviewer_id", user_name="reviewer_name")

    song_id = post_song(client, uid="creator_id", name="happy_song").json()["id"]
    album_id = post_album(client, uid="creator_id", songs_ids=[song_id]).json()["id"]

    block_song(client, song_id)

    response_post = post_review(
        client, uid="reviewer_id", album_id=album_id, text="my text", score=3
    )
    assert response_post.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"api_key": "key", "uid": "song_creator_id", "role": "admin"},
    )
    assert response_get.status_code == 200


def test_post_one_review_affects_album_score(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="reviewer_id", user_name="reviewer_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    post_review(client, "reviewer_id", album_id, "bad song", 2)

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"api_key": "key", "uid": "song_creator_id", "role": "admin"},
    )
    album = response_get.json()
    assert response_get.status_code == 200
    assert album["score"] == 2


def test_post_many_reviews_affects_score(client, custom_requests_mock):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="first_reviewer_id", user_name="first_reviewer_name")
    post_user(client, uid="second_reviewer_id", user_name="second_reviewer_name")

    album_id = post_album(client, uid="creator_id").json()["id"]
    post_review(client, "first_reviewer_id", album_id, "bad song", 2)
    post_review(client, "second_reviewer_id", album_id, "good song", 5)

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"api_key": "key", "uid": "song_creator_id", "role": "admin"},
    )
    album = response_get.json()
    assert response_get.status_code == 200
    assert album["score"] == 3.5


def test_user_with_two_reviews_in_different_albums_edits_one_review(
    client, custom_requests_mock
):
    post_user(client, uid="creator_id", user_name="creator_name")
    post_user(client, uid="reviewer_id", user_name="reviewer_name")

    album_id_1 = post_album(client, uid="creator_id").json()["id"]
    album_id_2 = post_album(client, uid="creator_id").json()["id"]

    post_review(client, "reviewer_id", album_id_1, "bad song", 2)
    post_review(client, "reviewer_id", album_id_2, "good song", 5)

    response_put = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id_2}/reviews/",
        json={"text": "I'm trying to change a review", "score": 3},
        headers={"api_key": "key", "uid": "reviewer_id"},
    )
    assert response_put.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id_2}/reviews/",
        headers={"api_key": "key", "uid": "reviewer_id"},
    )
    reviews = response_get.json()
    assert response_get.status_code == 200
    assert len(reviews) == 1
    assert reviews[0]["text"] == "I'm trying to change a review"
    assert reviews[0]["score"] == 3
