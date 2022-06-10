from tests.utils import API_VERSION_PREFIX
from tests.utils import post_song, post_user


def test_search_song_by_artist_without_created_songs(client, custom_requests_mock):
    post_user(client, "user_id", "user_name")

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?artist=artist_name", headers={"api_key": "key"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_song_by_artist_without_results(client, custom_requests_mock):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id", artists=["artist_name"])
    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?artist=another_artist", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_song_by_artist_exact_name_one_result(client, custom_requests_mock):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id", name="my_song_name", artists=["artist_name"])

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?artist=artist_name", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "my_song_name"


def test_search_song_by_artist_song_with_many_artists(client, custom_requests_mock):
    post_user(client, "user_id", "user_name")
    post_song(
        client,
        uid="user_id",
        name="my_song_name",
        artists=["artist_name_1", "artist_name_2", "artist_name_3"],
    )
    post_song(client, uid="user_id", name="another_song_name", artists=["bar"])

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?artist=artist_name_2", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_song_by_artist_substring_one_result(client, custom_requests_mock):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id", artists=["artist_name"])

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?artist=artist_na", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_song_by_artist_case_insensitive_one_result(
    client, custom_requests_mock
):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id", artists=["artist_name"])

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?artist=ArTISt_nAME", headers={"api_key": "key"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_song_by_artist_substring_case_insensitive_one_result(
    client, custom_requests_mock
):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id", artists=["artist_name"])

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?artist=ArTISt_Na", headers={"api_key": "key"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_song_by_artist_substring_case_insensitive_many_results(
    client, custom_requests_mock
):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id", name="first_song", artists=["artist_name"])
    post_song(
        client, uid="user_id", name="second_song", artists=["ANOTHER_ARTIST_NAME"]
    )
    post_song(client, uid="user_id", name="second_song", artists=["foo"])

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?artist=ArTISt_na", headers={"api_key": "key"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_search_song_by_genre_without_created_songs(client, custom_requests_mock):
    post_user(client, "user_id", "user_name")

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?genre=my_genre", headers={"api_key": "key"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_song_by_genre_without_results(client, custom_requests_mock):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id", genre="my_genre")

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?genre=another_genre", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_song_by_genre_exact_name_one_result(client, custom_requests_mock):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id", name="my_song_name", genre="my_genre")
    post_song(client, uid="user_id", name="another_song_name", genre="bar")

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?genre=my_genre", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "my_song_name"
    assert response.json()[0]["genre"] == "my_genre"


def test_search_song_by_genre_substring_one_result(client, custom_requests_mock):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id", name="my_song_name", genre="my_genre")
    post_song(client, uid="user_id", name="another_song_name", genre="bar")

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?genre=genr", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_song_by_genre_case_insensitive_one_result(client, custom_requests_mock):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id", name="my_song_name", genre="my_genre")
    post_song(client, uid="user_id", name="another_song_name", genre="bar")

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?genre=My_Genre", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_song_by_genre_substring_case_insensitive_one_result(
    client, custom_requests_mock
):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id", name="my_song_name", genre="my_genre")
    post_song(client, uid="user_id", name="another_song_name", genre="bar")

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?genre=GEN", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_song_by_genre_substring_case_insensitive_many_results(
    client, custom_requests_mock
):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id", genre="my_genre")
    post_song(client, uid="user_id", genre="MY_GENRE")
    post_song(client, uid="user_id", genre="foo")

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?genre=GEN", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_search_song_by_subscription_without_songs(client, custom_requests_mock):
    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?sub_level=0", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_song_by_subscription_without_results(client, custom_requests_mock):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id", name="my_song_name", sub_level=1)

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?sub_level=2", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_song_by_subscription_one_result(client, custom_requests_mock):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id", name="my_song_name", sub_level=1)
    post_song(client, uid="user_id", name="another_song_name", sub_level=2)

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?sub_level=2", headers={"api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "another_song_name"


def test_search_song_multiple_queries(client, custom_requests_mock):
    post_user(client, "user_id", "user_name")
    post_song(
        client,
        uid="user_id",
        artists=["my_artist_name"],
        name="first_song_name",
        genre="my_genre",
    )
    post_song(
        client,
        uid="user_id",
        artists=["my_artist_name"],
        name="second_song_name",
        genre="another_genre",
    )
    post_song(
        client,
        uid="user_id",
        artists=["bar"],
        name="third_song_name",
        genre="another_genre",
    )

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?creator=user_id&artist=my_artist_name&genre=my_genre",
        headers={"api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_song_by_name(client, custom_requests_mock):
    post_user(client, "user_id", "user_name")
    post_song(client, uid="user_id", name="my_song_name", sub_level=1)
    post_song(client, uid="user_id", name="another_song_name", sub_level=2)

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/?name=my_song_name",
        headers={"api_key": "key"},
    )
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "my_song_name"
