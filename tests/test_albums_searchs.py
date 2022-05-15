from tests.utils import API_VERSION_PREFIX
from tests.utils import post_album, post_user, post_song, post_album_with_song


def test_search_album_by_artist_without_created_songs(client):
    post_user(client, "user_id", "user_name")

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?artist=artist_name", headers={"api_key": "key"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_album_by_artist_without_results(client):
    post_user(client, "user_id", "user_name")
    song_id = post_song(client, uid="user_id", artists=["artist_name"]).json()["id"]

    post_album(client, uid="user_id", songs_ids=[song_id])
    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?artist=another_artist",
        headers={"api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_album_by_artist_exact_name_one_result(client):
    post_user(client, "user_id", "user_name")
    song_id = post_song(
        client, uid="user_id", name="my_song_name", artists=["artist_name"]
    ).json()["id"]

    post_album(client, uid="user_id", name="my_album_name", songs_ids=[song_id])

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?artist=artist_name", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "my_album_name"
    assert response.json()[0]["songs"][0]["name"] == "my_song_name"


def test_search_album_by_artist_song_with_many_artists(client):
    post_user(client, "user_id", "user_name")
    song_id_1 = post_song(
        client,
        uid="user_id",
        name="my_song_name",
        artists=["artist_name_1", "artist_name_2", "artist_name_3"],
    ).json()["id"]

    song_id_2 = post_song(
        client, uid="user_id", name="another_song_name", artists=["bar"]
    ).json()["id"]

    post_album(client, uid="user_id", name="my_album_name", songs_ids=[song_id_1])
    post_album(client, uid="user_id", name="another_album_name", songs_ids=[song_id_2])

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?artist=artist_name_2", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_album_by_artist_substring_one_result(client):
    post_user(client, "user_id", "user_name")
    song_id = post_song(client, uid="user_id", artists=["artist_name"]).json()["id"]
    post_album(client, uid="user_id", songs_ids=[song_id])

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?artist=artist_na", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_album_by_artist_case_insensitive_one_result(client):
    post_user(client, "user_id", "user_name")
    song_id = post_song(client, uid="user_id", artists=["artist_name"]).json()["id"]
    post_album(client, uid="user_id", songs_ids=[song_id])

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?artist=ArTISt_nAME", headers={"api_key": "key"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_album_by_artist_substring_case_insensitive_one_result(client):
    post_user(client, "user_id", "user_name")
    song_id = post_song(client, uid="user_id", artists=["artist_name"]).json()["id"]
    post_album(client, uid="user_id", songs_ids=[song_id])

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?artist=ArTISt_Na", headers={"api_key": "key"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_album_by_artist_substring_case_insensitive_many_results(client):
    post_user(client, "user_id", "user_name")
    song_id_1 = post_song(
        client, uid="user_id", name="first_song", artists=["artist_name", "bar"]
    ).json()["id"]
    song_id_2 = post_song(
        client, uid="user_id", name="second_song", artists=["ANOTHER_ARTIST_NAME"]
    ).json()["id"]
    song_id_3 = post_song(
        client, uid="user_id", name="second_song", artists=["foo"]
    ).json()["id"]

    post_album(client, uid="user_id", name="first_album", songs_ids=[song_id_1])
    post_album(client, uid="user_id", name="second_album", songs_ids=[song_id_2])
    post_album(client, uid="user_id", name="third_album", songs_ids=[song_id_3])

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?artist=ArTISt_na", headers={"api_key": "key"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert "third_album" != response.json()[0]["name"]
    assert "third_album" != response.json()[1]["name"]


def test_search_album_by_genre_without_created_songs(client):
    post_user(client, "user_id", "user_name")

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?genre=my_genre", headers={"api_key": "key"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_album_by_genre_without_results(client):
    post_user(client, "user_id", "user_name")
    song_id = post_song(client, uid="user_id", genre="my_genre").json()["id"]
    post_album(client, uid="user_id", genre="my_genre", songs_ids=[song_id])

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?genre=another_genre", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_album_by_genre_exact_name_one_result(client):
    post_user(client, "user_id", "user_name")
    post_album_with_song(
        client, uid="user_id", album_genre="my_album_genre", album_name="my_album_name"
    )

    post_album_with_song(
        client,
        uid="user_id",
        album_genre="another_album_genre",
        album_name="another_album_name",
    )

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?genre=my_album_genre", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "my_album_name"
    assert response.json()[0]["genre"] == "my_album_genre"


def test_search_album_by_genre_ignores_songs_genre(client):
    post_user(client, "user_id", "user_name")
    post_album_with_song(
        client, uid="user_id", album_genre="my_album_genre", album_name="my_album_name"
    )

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?genre=my_song_genre", headers={"api_key": "key"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_album_by_genre_substring_one_result(client):
    post_user(client, "user_id", "user_name")
    post_album_with_song(
        client, uid="user_id", album_name="my_album_name", album_genre="my_genre"
    )
    post_album_with_song(
        client, uid="user_id", album_name="another_album_name", album_genre="bar"
    )

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?genre=genr", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "my_album_name"


def test_search_album_by_genre_case_insensitive_one_result(client):
    post_user(client, "user_id", "user_name")
    post_album_with_song(
        client, uid="user_id", album_name="my_album_name", album_genre="my_genre"
    )
    post_album_with_song(
        client, uid="user_id", album_name="another_album_name", album_genre="bar"
    )

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?genre=My_Genre", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_album_by_genre_substring_case_insensitive_one_result(client):
    post_user(client, "user_id", "user_name")
    post_album_with_song(
        client, uid="user_id", album_name="my_album_name", album_genre="my_genre"
    )
    post_album_with_song(
        client, uid="user_id", album_name="another_album_name", album_genre="bar"
    )

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?genre=GEN", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_album_by_genre_substring_case_insensitive_many_results(client):
    post_user(client, "user_id", "user_name")
    post_album_with_song(client, uid="user_id", album_genre="my_genre")
    post_album_with_song(client, uid="user_id", album_genre="MY_GENRE")
    post_album_with_song(client, uid="user_id", album_genre="foo")

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?genre=GEN", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_search_album_by_subscription_without_songs(client):
    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?sub_level=0", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_album_by_subscription_without_results(client):
    post_user(client, "user_id", "user_name")
    post_album_with_song(client, uid="user_id", album_sub_level=0)

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?sub_level=2", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_album_by_subscription_one_result(client):
    post_user(client, "user_id", "user_name")
    post_album_with_song(
        client, uid="user_id", album_name="my_album_name", album_sub_level=1
    )
    post_album_with_song(
        client, uid="user_id", album_name="another_album_name", album_sub_level=2
    )

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?sub_level=2", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "another_album_name"


def test_search_album_by_subscription_ignores_song_sub_level(client):
    post_user(client, "user_id", "user_name")
    post_album_with_song(
        client,
        uid="user_id",
        album_name="my_album_name",
        album_sub_level=1,
        song_sub_level=0,
    )

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?sub_level=0", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_album_multiple_queries(client):
    post_user(client, "user_id", "user_name")
    post_album_with_song(
        client,
        uid="user_id",
        album_genre="my_genre",
        album_name="expected_album",
        album_sub_level=0,
    )
    post_album_with_song(
        client,
        uid="user_id",
        album_genre="my_genre",
        album_sub_level=1,
    )
    post_album_with_song(
        client,
        uid="user_id",
        album_genre="bar",
        album_sub_level=1,
    )

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/?creator=user_id&genre=my_genre&sub_level=0",
        headers={"api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "expected_album"
