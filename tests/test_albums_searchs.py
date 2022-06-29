from tests import utils
from tests.utils import API_VERSION_PREFIX
from tests.utils import post_album, post_user, post_song, post_album_with_song


def test_search_album_by_artist_without_created_songs(client, custom_requests_mock):
    post_user(client, "user_id")

    response = utils.search_albums(client, artist="artist_name")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 0


def test_search_album_by_artist_without_results(client, custom_requests_mock):
    post_user(client, "user_id")
    song_id = post_song(client, artists=["artist_name"])

    post_album(client, songs_ids=[song_id])
    response = utils.search_albums(client, artist="another_artist")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 0


def test_search_album_by_artist_exact_name_one_result(client, custom_requests_mock):
    post_user(client, "user_id")
    song_id = post_song(client, artists=["artist_name"])

    post_album(client, name="my_album_name", songs_ids=[song_id])

    response = utils.search_albums(client, artist="artist_name")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "my_album_name"


def test_search_album_by_artist_song_with_many_artists(client, custom_requests_mock):
    post_user(client, "user_id")

    song_id_1 = post_song(
        client,
        artists=["artist_name_1", "artist_name_2", "artist_name_3"],
    )

    song_id_2 = post_song(client, artists=["bar"])

    post_album(client, name="my_album_name", songs_ids=[song_id_1])
    post_album(client, name="another_album_name", songs_ids=[song_id_2])

    response = utils.search_albums(client, artist="artist_name_2")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 1


def test_search_album_by_artist_substring_one_result(client, custom_requests_mock):
    post_user(client, "user_id")
    song_id = post_song(client, uid="user_id", artists=["artist_name"])
    post_album(client, songs_ids=[song_id])

    response = utils.search_albums(client, artist="artist_name")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 1


def test_search_album_by_artist_case_insensitive_one_result(
    client, custom_requests_mock
):
    post_user(client, "user_id")
    song_id = post_song(client, uid="user_id", artists=["artist_name"])
    post_album(client, songs_ids=[song_id])

    response = utils.search_albums(client, artist="ArTISt_nAME")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 1


def test_search_album_by_artist_substring_case_insensitive_one_result(
    client, custom_requests_mock
):
    post_user(client, "user_id")
    song_id = post_song(client, artists=["artist_name"])
    post_album(client, songs_ids=[song_id])

    response = utils.search_albums(client, artist="ArTISt_Na")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 1


def test_search_album_by_artist_substring_case_insensitive_many_results(
    client, custom_requests_mock
):
    post_user(client, "user_id")
    song_id_1 = post_song(client, artists=["artist_name", "bar"])
    song_id_2 = post_song(client, artists=["ANOTHER_ARTIST_NAME"])
    song_id_3 = post_song(client, artists=["foo"])

    post_album(client, name="first_album", songs_ids=[song_id_1])
    post_album(client, name="second_album", songs_ids=[song_id_2])
    post_album(client, name="third_album", songs_ids=[song_id_3])

    response = utils.search_albums(client, artist="ArTISt_na")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 2
    assert "third_album" != albums[0]["name"]
    assert "third_album" != albums[1]["name"]


def test_search_album_by_genre_without_created_songs(client, custom_requests_mock):
    post_user(client, "user_id")

    response = utils.search_albums(client, genre="my_genre")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 0


def test_search_album_by_genre_without_results(client, custom_requests_mock):
    post_user(client, "user_id")
    song_id = post_song(client, genre="my_genre")
    post_album(client, genre="my_genre", songs_ids=[song_id])

    response = utils.search_albums(client, genre="another_genre")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 0


def test_search_album_by_genre_exact_name_one_result(client, custom_requests_mock):
    post_user(client, "user_id")
    post_album_with_song(
        client, album_genre="my_album_genre", album_name="my_album_name"
    )

    post_album_with_song(
        client,
        album_genre="another_album_genre",
        album_name="another_album_name",
    )

    response = utils.search_albums(client, genre="my_album_genre")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "my_album_name"
    assert albums[0]["genre"] == "my_album_genre"


def test_search_album_by_genre_ignores_songs_genre(client, custom_requests_mock):
    post_user(client, "user_id")
    post_album_with_song(
        client, album_genre="my_album_genre", album_name="my_album_name"
    )

    response = utils.search_albums(client, genre="my_song_genre")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 0


def test_search_album_by_genre_substring_one_result(client, custom_requests_mock):
    post_user(client, "user_id", "user_name")
    post_album_with_song(
        client, uid="user_id", album_name="my_album_name", album_genre="my_genre"
    )
    post_album_with_song(
        client, uid="user_id", album_name="another_album_name", album_genre="bar"
    )

    response = utils.search_albums(client, genre="genr")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "my_album_name"


def test_search_album_by_genre_case_insensitive_one_result(
    client, custom_requests_mock
):
    post_user(client, "user_id")
    post_album_with_song(client, album_name="my_album_name", album_genre="my_genre")
    post_album_with_song(client, album_name="another_album_name", album_genre="bar")

    response = utils.search_albums(client, genre="My_Genre")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "my_album_name"


def test_search_album_by_genre_substring_case_insensitive_one_result(
    client, custom_requests_mock
):
    post_user(client, "user_id")
    post_album_with_song(client, album_name="my_album_name", album_genre="my_genre")
    post_album_with_song(client, album_name="another_album_name", album_genre="bar")

    response = utils.search_albums(client, genre="GEN")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 1


def test_search_album_by_genre_substring_case_insensitive_many_results(
    client, custom_requests_mock
):
    post_user(client, "user_id")
    post_album_with_song(client, album_genre="my_genre")
    post_album_with_song(client, album_genre="MY_GENRE")
    post_album_with_song(client, album_genre="foo")

    response = utils.search_albums(client, genre="GEN")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 2


def test_search_album_multiple_queries(client, custom_requests_mock):
    post_user(client, "user_id")
    post_album_with_song(
        client,
        album_genre="my_genre",
        album_name="expected_album",
    )
    post_album_with_song(
        client,
        album_genre="my_genre",
    )
    post_album_with_song(
        client,
        album_genre="bar",
    )

    response = utils.search_albums(client, genre="my_genre", creator="user_id")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 2


def test_search_album_by_name(client, custom_requests_mock):
    post_user(client, "album_creator_id")
    post_album(client, name="my_album")

    response = utils.search_albums(client, name="ALBUM")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "my_album"
