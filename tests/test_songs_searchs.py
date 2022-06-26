from tests import utils
from tests.utils import API_VERSION_PREFIX
from tests.utils import post_song, post_user


def test_search_song_by_artist_without_created_songs(client, custom_requests_mock):
    response = utils.search_songs(client, artist="my_artist")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 0


def test_search_song_by_artist_without_results(client, custom_requests_mock):
    post_song(client, artists=["artist_name"])

    response = utils.search_songs(client, artist="another_artist")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 0


def test_search_song_by_artist_exact_name_one_result(client, custom_requests_mock):
    post_song(client, name="my_song_name", artists=["artist_name"])

    response = utils.search_songs(client, name="my_song_name")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "my_song_name"


def test_search_song_by_artist_song_with_many_artists(client, custom_requests_mock):
    post_song(
        client,
        name="my_song_name",
        artists=["artist_name_1", "artist_name_2", "artist_name_3"],
    )
    post_song(client, name="another_song_name", artists=["bar"])

    response = utils.search_songs(client, artist="artist_name_2")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 1


def test_search_song_by_artist_substring_one_result(client, custom_requests_mock):
    post_song(client, artists=["artist_name"])

    response = utils.search_songs(client, artist="artist_na")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 1


def test_search_song_by_artist_case_insensitive_one_result(
    client, custom_requests_mock
):
    post_song(client, artists=["artist_name"])

    response = utils.search_songs(client, artist="ArTISt_nAME")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 1


def test_search_song_by_artist_substring_case_insensitive_one_result(
    client, custom_requests_mock
):
    post_song(client, artists=["artist_name"])

    response = utils.search_songs(client, artist="ArTISt_Na")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 1


def test_search_song_by_artist_substring_case_insensitive_many_results(
    client, custom_requests_mock
):
    post_song(client, name="first_song", artists=["artist_name"])
    post_song(client, name="second_song", artists=["ANOTHER_ARTIST_NAME"])
    post_song(client, name="second_song", artists=["foo"])

    response = utils.search_songs(client, artist="ArTISt_na")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 2


def test_search_song_by_genre_without_created_songs(client, custom_requests_mock):
    response = utils.search_songs(client, genre="my_genre")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 0


def test_search_song_by_genre_without_results(client, custom_requests_mock):
    post_song(client, genre="my_genre")

    response = utils.search_songs(client, genre="another_genre")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 0


def test_search_song_by_genre_exact_name_one_result(client, custom_requests_mock):
    post_song(client, name="my_song_name", genre="my_genre")
    post_song(client, name="another_song_name", genre="bar")

    response = utils.search_songs(client, genre="my_genre")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "my_song_name"
    assert songs[0]["genre"] == "my_genre"


def test_search_song_by_genre_substring_one_result(client, custom_requests_mock):
    post_song(client, name="my_song_name", genre="my_genre")
    post_song(client, name="another_song_name", genre="bar")

    response = utils.search_songs(client, genre="genr")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 1


def test_search_song_by_genre_case_insensitive_one_result(client, custom_requests_mock):
    post_song(client, name="my_song_name", genre="my_genre")
    post_song(client, name="another_song_name", genre="bar")

    response = utils.search_songs(client, genre="My_Genre")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "my_song_name"


def test_search_song_by_genre_substring_case_insensitive_one_result(
    client, custom_requests_mock
):
    post_song(client, name="my_song_name", genre="my_genre")
    post_song(client, name="another_song_name", genre="bar")

    response = utils.search_songs(client, genre="GEN")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "my_song_name"


def test_search_song_by_genre_substring_case_insensitive_many_results(
    client, custom_requests_mock
):
    post_song(client, genre="my_genre")
    post_song(client, genre="MY_GENRE")
    post_song(client, genre="foo")

    response = utils.search_songs(client, genre="GEN")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 2


def test_search_song_by_subscription_without_songs(client, custom_requests_mock):
    response = utils.search_songs(client, sub_level=0)
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 0


def test_search_song_by_subscription_without_results(client, custom_requests_mock):
    post_song(client, name="my_song_name", sub_level=1)

    response = utils.search_songs(client, sub_level=0)
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 0


def test_search_song_by_subscription_one_result(client, custom_requests_mock):
    post_song(client, name="my_song_name", sub_level=1)
    post_song(client, name="another_song_name", sub_level=2)

    response = utils.search_songs(client, sub_level=2)
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "another_song_name"


def test_search_song_multiple_queries(client, custom_requests_mock):
    post_user(client, "user_id")
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

    response = utils.search_songs(
        client, artist="my_artist_name", creator="user_id", genre="my_genre"
    )
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 1


def test_search_song_by_name(client, custom_requests_mock):
    post_song(client, name="my_song_name")
    post_song(client, name="another_song_name")

    response = utils.search_songs(client, name="my_song_name")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "my_song_name"
