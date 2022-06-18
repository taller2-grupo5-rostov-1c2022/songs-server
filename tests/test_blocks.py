from tests import utils
from tests.utils import (
    API_VERSION_PREFIX,
    post_user,
    post_song,
    post_album,
    post_playlist,
    block_song,
)


def test_user_cannot_modify_blocked_status_of_song(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")
    song_id = post_song(client, uid="artist_id").json()["id"]

    response = client.put(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        data={"blocked": True},
        headers={"uid": "artist_id", "role": "listener", "api_key": "key"},
    )

    assert response.status_code == 403

    response_get = utils.get_song_by_id(client, song_id, role="admin")

    song = response_get.json()

    assert response_get.status_code == 200
    assert song["blocked"] is False


def test_admin_can_modify_blocked_status_of_song(client, custom_requests_mock):
    post_user(client, uid="admin_id", user_name="admin_name")
    post_user(client, uid="artist_id", user_name="artist_name")
    song_id = post_song(client, uid="artist_id").json()["id"]

    response_put = client.put(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        data={"blocked": True},
        headers={"uid": "admin_id", "role": "admin", "api_key": "key"},
    )
    assert response_put.status_code == 200


def test_listener_get_not_blocked_song_by_id(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")

    song_id = post_song(client, uid="artist_id").json()["id"]

    response = utils.get_song_by_id(client, song_id, role="listener")

    assert response.status_code == 200


def test_listener_get_blocked_song_by_id_should_fail(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")

    song_id = post_song(client, uid="artist_id", blocked=True).json()["id"]

    response = utils.get_song_by_id(client, song_id, role="listener")

    assert response.status_code == 404


def test_artist_get_blocked_song_by_id_should_fail(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")
    song_id = post_song(client, uid="artist_id", blocked=True).json()["id"]

    response = utils.get_song_by_id(client, song_id, role="artist")

    assert response.status_code == 404


def test_user_without_role_get_blocked_song_by_id_should_fail(
    client, custom_requests_mock
):
    post_user(client, uid="artist_id", user_name="artist_name")
    song_id = post_song(client, uid="artist_id", blocked=True).json()["id"]

    response = utils.get_song_by_id(client, song_id)

    assert response.status_code == 404


def test_admin_get_blocked_song_by_id(client, custom_requests_mock):
    post_user(client, uid="admin_id", user_name="admin_name")
    song_id = post_song(client, uid="admin_id", blocked=True).json()["id"]

    response = utils.get_song_by_id(client, song_id, role="admin")

    assert response.status_code == 200


def test_listener_get_all_songs_returns_only_not_blocked_songs(
    client, custom_requests_mock
):
    post_user(client, uid="artist_id", user_name="artist_name")

    post_song(client, uid="artist_id", name="not_blocked_song", blocked=False)
    post_song(client, uid="artist_id", name="blocked_song", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/",
        headers={"role": "listener", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "not_blocked_song"


def test_admin_get_all_songs_returns_blocked_and_not_blocked_songs(
    client, custom_requests_mock
):
    post_user(client, uid="admin_id", user_name="admin_name")
    post_song(client, uid="admin_id", name="not_blocked_song", blocked=False)
    post_song(client, uid="admin_id", name="blocked_song", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/", headers={"role": "admin", "api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_admin_get_song_by_id_indicates_if_song_is_blocked(
    client, custom_requests_mock
):
    post_user(client, uid="admin_id", user_name="admin_name")

    song_id = post_song(client, uid="admin_id", blocked=True).json()["id"]

    response = utils.get_song_by_id(client, song_id, role="admin")

    assert response.status_code == 200
    assert response.json()["blocked"] is True


def test_artist_get_my_songs_returns_blocked_songs(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")

    post_song(client, uid="artist_id", name="not_blocked_song", blocked=False)
    post_song(client, uid="artist_id", name="blocked_song", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/my_songs/",
        headers={"uid": "artist_id", "role": "artist", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_song_by_id_invalid_role(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")

    song_id = post_song(client, uid="artist_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"role": "an_invalid_role", "api_key": "key"},
    )

    assert response.status_code == 422


def test_get_songs_invalid_role(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")
    post_song(client, uid="artist_id", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/",
        headers={"role": "an_invalid_role", "api_key": "key"},
    )

    assert response.status_code == 422


def test_user_cannot_modify_blocked_status_of_album(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")
    album_id = post_album(client, uid="artist_id").json()["id"]

    response = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        data={"blocked": True},
        headers={"uid": "artist_id", "role": "listener", "api_key": "key"},
    )
    assert response.status_code == 403


def test_admin_can_modify_blocked_status_of_album(client, custom_requests_mock):
    post_user(client, uid="admin_id", user_name="admin_name")
    post_user(client, uid="artist_id", user_name="artist_name")
    album_id = post_album(client, uid="artist_id").json()["id"]

    response_put = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        data={"blocked": True},
        headers={"uid": "admin_id", "role": "admin", "api_key": "key"},
    )
    assert response_put.status_code == 200


def test_listener_get_not_blocked_album_by_id(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")

    album_id = post_album(
        client, name="my_album_name", uid="artist_id", blocked=False
    ).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"role": "listener", "api_key": "key"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "my_album_name"


def test_listener_get_blocked_album_by_id_should_fail(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")

    album_id = post_album(
        client, name="my_album_name", uid="artist_id", blocked=True
    ).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"role": "listener", "api_key": "key"},
    )

    assert response.status_code == 404


def test_admin_get_blocked_album_by_id(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")

    album_id = post_album(
        client, name="my_album_name", uid="artist_id", blocked=True
    ).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"role": "admin", "api_key": "key"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "my_album_name"


def test_listener_get_all_albums_returns_only_not_blocked_albums(
    client, custom_requests_mock
):
    post_user(client, uid="artist_id", user_name="artist_name")

    post_album(client, uid="artist_id", name="not_blocked_album", blocked=False)
    post_album(client, uid="artist_id", name="blocked_album", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/",
        headers={"role": "listener", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "not_blocked_album"


def test_admin_get_all_albums_returns_blocked_and_not_blocked_albums(
    client, custom_requests_mock
):
    post_user(client, uid="artist_id", user_name="artist_name")

    post_album(client, uid="artist_id", name="not_blocked_album", blocked=False)
    post_album(client, uid="artist_id", name="blocked_album", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/",
        headers={"role": "admin", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_admin_get_album_by_id_indicates_if_album_is_blocked(
    client, custom_requests_mock
):
    post_user(client, uid="admin_id", user_name="admin_name")

    album_id = post_album(
        client, uid="admin_id", name="not_blocked_album", blocked=True
    ).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"role": "admin", "api_key": "key"},
    )

    assert response.status_code == 200
    assert response.json()["blocked"] is True


def test_artist_get_my_albums_returns_blocked_albums(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")

    post_album(client, uid="artist_id", name="not_blocked_album", blocked=False)
    post_album(client, uid="artist_id", name="blocked_album", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/my_albums/",
        headers={"uid": "artist_id", "role": "artist", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_album_by_id_invalid_role(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")

    album_id = post_album(client, uid="artist_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"role": "an_invalid_role", "api_key": "key"},
    )

    assert response.status_code == 422


def test_get_albums_invalid_role(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")
    post_album(client, uid="artist_id", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/",
        headers={"role": "an_invalid_role", "api_key": "key"},
    )

    assert response.status_code == 422


def test_listener_get_album_by_id_with_blocked_songs_should_retrieve_not_blocked_songs(
    client, custom_requests_mock
):
    post_user(client, uid="artist_id", user_name="artist_name")
    # The song is blocked after the album is created
    song_id_1 = post_song(
        client, uid="artist_id", name="blocked_song", blocked=False
    ).json()["id"]

    song_id_2 = post_song(
        client, uid="artist_id", name="not_blocked_song", blocked=False
    ).json()["id"]

    album_id = post_album(
        client,
        uid="artist_id",
        name="blocked_song",
        songs_ids=[song_id_1, song_id_2],
        blocked=False,
    )
    block_song(client, song_id=song_id_1)

    album_id = album_id.json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"role": "listener", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()["songs"]) == 1
    assert response.json()["songs"][0]["name"] == "not_blocked_song"


def test_listener_get_all_albums_return_only_not_blocked_songs(
    client, custom_requests_mock
):
    post_user(client, uid="artist_id", user_name="artist_name")

    song_id_1 = post_song(
        client, uid="artist_id", name="blocked_song", blocked=False
    ).json()["id"]

    song_id_2 = post_song(
        client, uid="artist_id", name="not_blocked_song", blocked=False
    ).json()["id"]

    post_album(
        client,
        uid="artist_id",
        songs_ids=[song_id_1, song_id_2],
        blocked=False,
    )
    block_song(client, song_id=song_id_1)

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/",
        headers={"role": "listener", "api_key": "key"},
    )

    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 1
    assert len(albums[0]["songs"]) == 1
    songs = albums[0]["songs"]
    assert songs[0]["name"] == "not_blocked_song"


def test_listener_get_album_by_id_with_blocked_songs_should_not_remove_song(
    client, custom_requests_mock
):
    # This is a white box test

    # The song is blocked after the album is created
    post_user(client, uid="artist_id", user_name="artist_name")
    song_id_1 = post_song(
        client, uid="artist_id", name="blocked_song", blocked=False
    ).json()["id"]
    song_id_2 = post_song(
        client, uid="artist_id", name="not_blocked_song", blocked=False
    ).json()["id"]

    album_id = post_album(
        client, uid="artist_id", songs_ids=[song_id_1, song_id_2], blocked=False
    ).json()["id"]
    block_song(client, song_id_1)

    client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"role": "listener", "api_key": "key"},
    )

    response_get_song = utils.get_song_by_id(client, song_id_1, role="admin")
    assert response_get_song.status_code == 200


def test_user_cannot_modify_blocked_status_of_playlist(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")
    playlist_id = post_playlist(client, uid="artist_id").json()["id"]

    response = client.put(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        data={"blocked": True},
        headers={"uid": "artist_id", "role": "listener", "api_key": "key"},
    )
    assert response.status_code == 403


def test_admin_can_modify_blocked_status_of_playlist(client, custom_requests_mock):
    post_user(client, uid="admin_id", user_name="admin_name")
    post_user(client, uid="artist_id", user_name="artist_name")
    playlist_id = post_playlist(client, uid="artist_id").json()["id"]

    response_put = client.put(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        data={"blocked": True},
        headers={"uid": "admin_id", "role": "admin", "api_key": "key"},
    )
    assert response_put.status_code == 200


def test_listener_get_not_blocked_playlist_by_id(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")

    playlist_id = post_playlist(client, uid="artist_id", blocked=False).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"role": "listener", "api_key": "key"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "playlist_name"


def test_listener_get_blocked_playlist_by_id_should_fail(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")

    playlist_id = post_playlist(client, uid="artist_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"role": "listener", "api_key": "key"},
    )

    assert response.status_code == 404


def test_admin_get_blocked_playlist_by_id(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")

    playlist_id = post_playlist(client, uid="artist_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"role": "admin", "api_key": "key"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "playlist_name"


def test_listener_get_all_playlists_returns_only_not_blocked_playlists(
    client, custom_requests_mock
):
    post_user(client, uid="artist_id", user_name="artist_name")

    post_playlist(
        client, uid="artist_id", playlist_name="not_blocked_playlist", blocked=False
    )
    post_playlist(client, uid="artist_id", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/",
        headers={"role": "listener", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "not_blocked_playlist"


def test_admin_get_all_playlists_returns_blocked_and_not_blocked_playlists(
    client, custom_requests_mock
):
    post_user(client, uid="artist_id", user_name="artist_name")

    post_playlist(client, uid="artist_id", blocked=False)
    post_playlist(client, uid="artist_id", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/",
        headers={"role": "admin", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_admin_get_playlist_by_id_indicates_if_playlist_is_blocked(
    client, custom_requests_mock
):
    post_user(client, uid="admin_id", user_name="admin_name")

    playlist_id = post_playlist(client, uid="admin_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"role": "admin", "api_key": "key"},
    )

    assert response.status_code == 200
    assert response.json()["blocked"] is True


def test_artist_get_my_playlists_returns_blocked_playlists(
    client, custom_requests_mock
):
    post_user(client, uid="artist_id", user_name="artist_name")

    post_playlist(client, uid="artist_id", blocked=False)
    post_playlist(client, uid="artist_id", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/my_playlists/",
        headers={"uid": "artist_id", "role": "artist", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_playlist_by_id_invalid_role(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")

    playlist_id = post_playlist(client, uid="artist_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"role": "an_invalid_role", "api_key": "key"},
    )

    assert response.status_code == 422


def test_get_playlists_invalid_role(client, custom_requests_mock):
    post_user(client, uid="artist_id", user_name="artist_name")
    post_playlist(client, uid="artist_id", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/",
        headers={"role": "an_invalid_role", "api_key": "key"},
    )

    assert response.status_code == 422


def test_listener_get_playlist_by_id_with_blocked_songs_should_retrieve_not_blocked_songs(
    client, custom_requests_mock
):
    post_user(client, uid="artist_id", user_name="artist_name")
    # The song is blocked after the playlist is created
    song_id_1 = post_song(
        client, uid="artist_id", name="blocked_song", blocked=False
    ).json()["id"]
    song_id_2 = post_song(
        client, uid="artist_id", name="not_blocked_song", blocked=False
    ).json()["id"]

    playlist_id = post_playlist(
        client, uid="artist_id", songs_ids=[song_id_1, song_id_2], blocked=False
    ).json()["id"]

    block_song(client, song_id_1)

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"role": "listener", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()["songs"]) == 1
    assert response.json()["songs"][0]["name"] == "not_blocked_song"


def test_listener_get_playlist_by_id_with_blocked_songs_should_not_remove_song(
    client, custom_requests_mock
):
    # This is a white box test

    post_user(client, uid="admin_id", user_name="admin_name")
    post_user(client, uid="artist_id", user_name="artist_name")
    # The song is blocked after the playlist is created
    song_id_1 = post_song(
        client, uid="artist_id", name="blocked_song", blocked=False
    ).json()["id"]
    song_id_2 = post_song(
        client, uid="artist_id", name="not_blocked_song", blocked=False
    ).json()["id"]

    playlist_id = post_playlist(
        client, uid="artist_id", songs_ids=[song_id_1, song_id_2], blocked=False
    ).json()["id"]
    block_song(client, song_id_1)

    client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"role": "listener", "api_key": "key"},
    )

    response_get_song = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id_1}",
        headers={"role": "admin", "api_key": "key", "uid": "admin_id"},
    )
    assert response_get_song.status_code == 200
    assert response_get_song.json()["blocked"] is True


def test_listener_edit_album_with_blocked_song_does_not_modify_blocked_song(
    client, custom_requests_mock
):
    post_user(client, uid="artist_id", user_name="artist_name")
    post_user(client, uid="admin_id", user_name="admin_name")

    song_id = post_song(
        client, uid="artist_id", name="blocked_song", blocked=False
    ).json()["id"]
    album_id = post_album(client, "artist_id", songs_ids=[song_id]).json()["id"]
    block_song(client, song_id)

    response_update = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        data={"name": "updated_test_album", "songs_ids": "[]"},
        headers={"api_key": "key", "uid": "artist_id"},
    )
    assert response_update.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"api_key": "key", "uid": "admin_id", "role": "admin"},
    )
    album = response_get.json()

    assert response_get.status_code == 200
    assert len(album["songs"]) == 1
    assert album["name"] == "updated_test_album"
    assert album["songs"][0]["blocked"] is True


def test_admin_edit_album_can_modify_blocked_song(client, custom_requests_mock):
    post_user(client, uid="admin_id", user_name="admin_name")
    post_user(client, uid="another_admin_id", user_name="another_admin_name")

    song_id = post_song(
        client, uid="admin_id", name="blocked_song", blocked=False
    ).json()["id"]
    album_id = post_album(client, "admin_id", songs_ids=[song_id]).json()["id"]
    block_song(client, song_id)

    response_update = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        data={"name": "updated_test_album", "songs_ids": "[]"},
        headers={"api_key": "key", "uid": "admin_id", "role": "admin"},
    )
    assert response_update.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"api_key": "key", "uid": "another_admin_id", "role": "admin"},
    )
    album = response_get.json()

    assert response_get.status_code == 200
    assert len(album["songs"]) == 0


def test_listener_edit_playlist_with_blocked_song_does_not_modify_blocked_song(
    client, custom_requests_mock
):
    post_user(client, uid="artist_id", user_name="artist_name")

    song_id = post_song(
        client, uid="artist_id", name="blocked_song", blocked=False
    ).json()["id"]

    playlist_id = post_playlist(client, "artist_id", songs_ids=[song_id]).json()["id"]
    block_song(client, song_id)

    response_update = client.put(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        data={"name": "updated_test_playlist", "songs_ids": "[]"},
        headers={"api_key": "key", "uid": "artist_id"},
    )
    assert response_update.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"api_key": "key", "uid": "admin_id", "role": "admin"},
    )
    playlist = response_get.json()

    assert response_get.status_code == 200
    assert playlist["name"] == "updated_test_playlist"
    assert len(playlist["songs"]) == 1
    assert playlist["songs"][0]["blocked"] is True


def test_listener_remove_blocked_song_from_playlist_does_not_remove_it(
    client, custom_requests_mock
):
    post_user(client, uid="artist_id", user_name="artist_name")
    post_user(client, uid="listener_id", user_name="listener_name")

    song_id = post_song(
        client, uid="artist_id", name="blocked_song", blocked=False
    ).json()["id"]
    playlist_id = post_playlist(client, "listener_id", songs_ids=[song_id]).json()["id"]
    block_song(client, song_id)

    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}/songs/{song_id}/",
        headers={"api_key": "key", "uid": "listener_id"},
    )

    assert response_delete.status_code == 404


def test_admin_remove_blocked_song_from_playlist_removes_it(
    client, custom_requests_mock
):
    post_user(client, uid="admin_id", user_name="admin_name")
    post_user(client, uid="creator_id", user_name="creator_name")

    song_id = post_song(
        client, uid="creator_id", name="blocked_song", blocked=False
    ).json()["id"]
    playlist_id = post_playlist(client, "creator_id", songs_ids=[song_id]).json()["id"]
    block_song(client, song_id)

    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}/songs/{song_id}/",
        headers={"api_key": "key", "uid": "admin_id", "role": "admin"},
    )
    assert response_delete.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"api_key": "key", "uid": "admin_id", "role": "admin"},
    )
    playlist = response_get.json()

    assert len(playlist["songs"]) == 0
