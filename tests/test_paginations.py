from tests import utils
from src.main import API_VERSION_PREFIX


def test_get_albums_first_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_album(client, "user_id", "album_1")
    utils.post_album(client, "user_id", "album_2")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/",
        params={"page": 0, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_1"


def test_get_albums_second_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_album(client, "user_id", "album_1")
    utils.post_album(client, "user_id", "album_2")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/",
        params={"page": 1, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_2"


def test_get_albums_page_bigger_than_total(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_album(client, "user_id", "album_1")
    utils.post_album(client, "user_id", "album_2")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/",
        params={"page": 2, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 0


def test_get_albums_size_bigger_than_total(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_album(client, "user_id", "album_1")
    utils.post_album(client, "user_id", "album_2")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/",
        params={"page": 0, "size": 2},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 2
    assert albums[0]["name"] == "album_1"
    assert albums[1]["name"] == "album_2"


def test_get_albums_with_songs_first_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    song_id_1 = utils.post_song(client, "user_id", "song_1").json()["id"]
    song_id_2 = utils.post_song(client, "user_id", "song_2").json()["id"]
    song_id_3 = utils.post_song(client, "user_id", "song_3").json()["id"]

    utils.post_album(client, "user_id", "album_1", songs_ids=[song_id_1, song_id_2])
    utils.post_album(client, "user_id", "album_2", songs_ids=[song_id_3])

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/",
        params={"page": 0, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_1"


def test_get_albums_with_songs_second_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    song_id_1 = utils.post_song(client, "user_id", "song_1").json()["id"]
    song_id_2 = utils.post_song(client, "user_id", "song_2").json()["id"]
    song_id_3 = utils.post_song(client, "user_id", "song_3").json()["id"]

    utils.post_album(client, "user_id", "album_1", songs_ids=[song_id_1, song_id_2])
    utils.post_album(client, "user_id", "album_2", songs_ids=[song_id_3])

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/",
        params={"page": 1, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_2"


def test_get_my_albums_first_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_album(client, "user_id", "album_1")
    utils.post_album(client, "user_id", "album_2")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/my_albums/",
        params={"page": 0, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_1"


def test_get_my_albums_second_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_album(client, "user_id", "album_1")
    utils.post_album(client, "user_id", "album_2")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/my_albums/",
        params={"page": 1, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_2"


def test_get_playlists_first_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_playlist(client, "user_id", "playlist_1")
    utils.post_playlist(client, "user_id", "playlist_2")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/",
        params={"page": 0, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    playlists = response_get.json()
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_1"


def test_get_playlists_second_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_playlist(client, "user_id", "playlist_1")
    utils.post_playlist(client, "user_id", "playlist_2")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/",
        params={"page": 1, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    playlists = response_get.json()
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_2"


def test_get_my_playlists_first_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_playlist(client, "user_id", "playlist_1")
    utils.post_playlist(client, "user_id", "playlist_2")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/my_playlists/",
        params={"page": 0, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    playlists = response_get.json()
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_1"


def test_get_my_playlists_second_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_playlist(client, "user_id", "playlist_1")
    utils.post_playlist(client, "user_id", "playlist_2")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/my_playlists/",
        params={"page": 0, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    playlists = response_get.json()
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_1"


def test_get_playlists_with_songs_first_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    song_id_1 = utils.post_song(client, "user_id", "song_1").json()["id"]
    song_id_2 = utils.post_song(client, "user_id", "song_2").json()["id"]
    song_id_3 = utils.post_song(client, "user_id", "song_3").json()["id"]

    utils.post_playlist(
        client, "user_id", "playlist_1", songs_ids=[song_id_1, song_id_2]
    )
    utils.post_playlist(client, "user_id", "playlist_2", songs_ids=[song_id_3])

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/",
        params={"page": 0, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    playlists = response_get.json()
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_1"


def test_get_playlists_with_songs_second_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    song_id_1 = utils.post_song(client, "user_id", "song_1").json()["id"]
    song_id_2 = utils.post_song(client, "user_id", "song_2").json()["id"]
    song_id_3 = utils.post_song(client, "user_id", "song_3").json()["id"]

    utils.post_playlist(
        client, "user_id", "playlist_1", songs_ids=[song_id_1, song_id_2]
    )
    utils.post_playlist(client, "user_id", "playlist_2", songs_ids=[song_id_3])

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/",
        params={"page": 1, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    playlists = response_get.json()
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_2"


def test_get_songs_first_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_song(client, "user_id", "song_1")
    utils.post_song(client, "user_id", "song_2")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/songs/",
        params={"page": 0, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    songs = response_get.json()
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_1"


def test_get_songs_second_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_song(client, "user_id", "song_1")
    utils.post_song(client, "user_id", "song_2")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/songs/",
        params={"page": 1, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    songs = response_get.json()
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_2"


def test_get_songs_filtered_by_name_first_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_song(client, "user_id", "foo")
    utils.post_song(client, "user_id", "song_1")
    utils.post_song(client, "user_id", "song_2")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/songs/",
        params={"page": 0, "size": 1, "name": "song"},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    songs = response_get.json()
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_1"


def test_get_songs_filtered_by_name_second_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_song(client, "user_id", "foo")
    utils.post_song(client, "user_id", "song_1")
    utils.post_song(client, "user_id", "song_2")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/songs/",
        params={"page": 1, "size": 1, "name": "song"},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    songs = response_get.json()
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_2"


def test_get_albums_filtered_by_artist_first_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    song_id_1 = utils.post_song(client, "user_id", "song_1", artists=["foo"]).json()[
        "id"
    ]
    song_id_2 = utils.post_song(
        client, "user_id", "song_2", artists=["artist_1"]
    ).json()["id"]
    song_id_3 = utils.post_song(
        client, "user_id", "song_2", artists=["artist_1"]
    ).json()["id"]

    utils.post_album(client, "user_id", "album_1", songs_ids=[song_id_1, song_id_2])
    utils.post_album(client, "user_id", "album_2", songs_ids=[song_id_3])

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/",
        params={"page": 0, "size": 1, "artist": "artist_1"},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_1"


def test_get_albums_filtered_by_artist_second_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    song_id_1 = utils.post_song(client, "user_id", "song_1", artists=["foo"]).json()[
        "id"
    ]
    song_id_2 = utils.post_song(
        client, "user_id", "song_2", artists=["artist_1"]
    ).json()["id"]
    song_id_3 = utils.post_song(
        client, "user_id", "song_2", artists=["artist_1"]
    ).json()["id"]

    utils.post_album(client, "user_id", "album_1", songs_ids=[song_id_1, song_id_2])
    utils.post_album(client, "user_id", "album_2", songs_ids=[song_id_3])

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/",
        params={"page": 1, "size": 1, "artist": "artist_1"},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_2"


def test_get_playlists_filtered_by_colab_first_page(client, custom_requests_mock):
    utils.post_user(client, "user_playlist_owner", "Ricardito")
    utils.post_user(client, "user_playlist_colab", "Fernandito")
    utils.post_user(client, "foo_id", "foo_name")

    utils.post_playlist(client, "user_playlist_owner", "playlist_1")
    utils.post_playlist(
        client, "user_playlist_owner", "playlist_2", colabs_ids=["user_playlist_colab"]
    )
    utils.post_playlist(
        client, "user_playlist_owner", "playlist_3", colabs_ids=["user_playlist_colab"]
    )

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/",
        params={"page": 0, "size": 1, "colab": "user_playlist_colab"},
        headers={"api_key": "key", "uid": "user_playlist_owner"},
        with_pagination=True,
    )

    playlists = response_get.json()
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_2"


def test_get_playlists_filtered_by_colab_second_page(client, custom_requests_mock):
    utils.post_user(client, "user_playlist_owner", "Ricardito")
    utils.post_user(client, "user_playlist_colab", "Fernandito")
    utils.post_user(client, "foo_id", "foo_name")

    utils.post_playlist(client, "user_playlist_owner", "playlist_1")
    utils.post_playlist(
        client, "user_playlist_owner", "playlist_2", colabs_ids=["user_playlist_colab"]
    )
    utils.post_playlist(
        client, "user_playlist_owner", "playlist_3", colabs_ids=["user_playlist_colab"]
    )

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/",
        params={"page": 1, "size": 1, "colab": "user_playlist_colab"},
        headers={"api_key": "key", "uid": "user_playlist_owner"},
        with_pagination=True,
    )

    playlists = response_get.json()
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_3"


def test_get_songs_with_blocked_songs_first_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_song(client, "user_id", "song_1")
    utils.post_song(client, "user_id", "song_2", blocked=True)
    utils.post_song(client, "user_id", "song_3")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/songs/",
        params={"page": 0, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    songs = response_get.json()
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_1"


def test_get_songs_with_blocked_songs_second_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_song(client, "user_id", "song_1")
    utils.post_song(client, "user_id", "song_2", blocked=True)
    utils.post_song(client, "user_id", "song_3")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/songs/",
        params={"page": 1, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    songs = response_get.json()
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_3"


def test_get_my_songs_first_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_song(client, "user_id", "song_1")
    utils.post_song(client, "user_id", "song_2")
    utils.post_song(client, "user_id", "song_3")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/my_songs/",
        params={"page": 0, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    songs = response_get.json()
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_1"


def test_get_my_songs_second_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_song(client, "user_id", "song_1")
    utils.post_song(client, "user_id", "song_2")
    utils.post_song(client, "user_id", "song_3")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/my_songs/",
        params={"page": 1, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    songs = response_get.json()
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_2"


def test_get_my_songs_with_own_blocked_songs_first_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_song(client, "user_id", "song_1")
    utils.post_song(client, "user_id", "song_2", blocked=True)
    utils.post_song(client, "user_id", "song_3")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/my_songs/",
        params={"page": 0, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    songs = response_get.json()
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_1"


def test_get_my_songs_with_blocked_songs_second_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")

    utils.post_song(client, "user_id", "song_1")
    utils.post_song(client, "user_id", "song_2", blocked=True)
    utils.post_song(client, "user_id", "song_3")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/my_songs/",
        params={"page": 1, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    songs = response_get.json()
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_2"


def test_get_my_songs_with_blocked_songs_of_another_user_first_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")
    utils.post_user(client, "user_id_2", "user_name_2")

    utils.post_song(client, "user_id", "song_1")
    utils.post_song(client, "user_id_2", "song_2", blocked=True)
    utils.post_song(client, "user_id", "song_3")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/my_songs/",
        params={"page": 0, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    songs = response_get.json()
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_1"


def test_get_my_songs_with_blocked_songs_of_another_user_second_page(client, custom_requests_mock):
    utils.post_user(client, "user_id", "user_name")
    utils.post_user(client, "user_id_2", "user_name_2")

    utils.post_song(client, "user_id", "song_1")
    utils.post_song(client, "user_id_2", "song_2", blocked=True)
    utils.post_song(client, "user_id", "song_3")

    response_get = client.get(
        f"{API_VERSION_PREFIX}/my_songs/",
        params={"page": 1, "size": 1},
        headers={"api_key": "key", "uid": "user_id"},
        with_pagination=True,
    )

    songs = response_get.json()
    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_3"
