from tests.utils import (
    API_VERSION_PREFIX,
    post_user,
    post_song,
    post_album,
    post_playlist,
    block_song,
)


def test_user_cannot_modify_blocked_status_of_song(client):
    post_user(client, uid="artist_id", user_name="artist_name")
    song_id = post_song(client, uid="artist_id").json()["id"]

    response = client.put(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        data={"blocked": True},
        headers={"uid": "artist_id", "role": "listener", "api_key": "key"},
    )

    assert response.status_code == 403

    response_get = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        data={"blocked": True},
        headers={"role": "admin", "api_key": "key"},
    )
    song = response_get.json()

    assert response_get.status_code == 200
    assert song["blocked"] is False


def test_admin_can_modify_blocked_status_of_song(client):
    post_user(client, uid="admin_id", user_name="admin_name")
    post_user(client, uid="artist_id", user_name="artist_name")
    song_id = post_song(client, uid="artist_id").json()["id"]

    response_put = client.put(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        data={"blocked": True},
        headers={"uid": "admin_id", "role": "admin", "api_key": "key"},
    )
    assert response_put.status_code == 200


def test_listener_get_not_blocked_song_by_id(client):
    post_user(client, uid="artist_id", user_name="artist_name")

    song_id = post_song(client, uid="artist_id").json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"role": "listener", "api_key": "key"},
    )

    assert response.status_code == 200


def test_listener_get_blocked_song_by_id_should_fail(client):
    post_user(client, uid="artist_id", user_name="artist_name")

    song_id = post_song(client, uid="artist_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"role": "listener", "api_key": "key"},
    )

    assert response.status_code == 403


def test_artist_get_blocked_song_by_id_should_fail(client):
    post_user(client, uid="artist_id", user_name="artist_name")
    song_id = post_song(client, uid="artist_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"role": "artist", "api_key": "key"},
    )

    assert response.status_code == 403


def test_user_without_role_get_blocked_song_by_id_should_fail(client):
    post_user(client, uid="artist_id", user_name="artist_name")
    song_id = post_song(client, uid="artist_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}", headers={"api_key": "key"}
    )

    assert response.status_code == 403


def test_admin_get_blocked_song_by_id(client):
    post_user(client, uid="admin_id", user_name="admin_name")
    song_id = post_song(client, uid="admin_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"role": "admin", "api_key": "key"},
    )

    assert response.status_code == 200


def test_listener_get_all_songs_returns_only_not_blocked_songs(client):
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


def test_admin_get_all_songs_returns_blocked_and_not_blocked_songs(client):
    post_user(client, uid="admin_id", user_name="admin_name")
    post_song(client, uid="admin_id", name="not_blocked_song", blocked=False)
    post_song(client, uid="admin_id", name="blocked_song", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/", headers={"role": "admin", "api_key": "key"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_admin_get_song_by_id_indicates_if_song_is_blocked(client):
    post_user(client, uid="admin_id", user_name="admin_name")

    song_id = post_song(client, uid="admin_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"role": "admin", "api_key": "key"},
    )

    assert response.status_code == 200
    assert response.json()["blocked"] is True


def test_artist_get_my_songs_returns_blocked_songs(client):
    post_user(client, uid="artist_id", user_name="artist_name")

    post_song(client, uid="artist_id", name="not_blocked_song", blocked=False)
    post_song(client, uid="artist_id", name="blocked_song", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/my_songs/",
        headers={"uid": "artist_id", "role": "artist", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_song_by_id_invalid_role(client):
    post_user(client, uid="artist_id", user_name="artist_name")

    song_id = post_song(client, uid="artist_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"role": "an_invalid_role", "api_key": "key"},
    )

    assert response.status_code == 422


def test_get_songs_invalid_role(client):
    post_user(client, uid="artist_id", user_name="artist_name")
    post_song(client, uid="artist_id", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/",
        headers={"role": "an_invalid_role", "api_key": "key"},
    )

    assert response.status_code == 422


def test_user_cannot_modify_blocked_status_of_album(client):
    post_user(client, uid="artist_id", user_name="artist_name")
    album_id = post_album(client, uid="artist_id").json()["id"]

    response = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        data={"blocked": True},
        headers={"uid": "artist_id", "role": "listener", "api_key": "key"},
    )
    assert response.status_code == 403


def test_admin_can_modify_blocked_status_of_album(client):
    post_user(client, uid="admin_id", user_name="admin_name")
    post_user(client, uid="artist_id", user_name="artist_name")
    album_id = post_album(client, uid="artist_id").json()["id"]

    response_put = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        data={"blocked": True},
        headers={"uid": "admin_id", "role": "admin", "api_key": "key"},
    )
    assert response_put.status_code == 200


def test_listener_get_not_blocked_album_by_id(client):
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


def test_listener_get_blocked_album_by_id_should_fail(client):
    post_user(client, uid="artist_id", user_name="artist_name")

    album_id = post_album(
        client, name="my_album_name", uid="artist_id", blocked=True
    ).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"role": "listener", "api_key": "key"},
    )

    assert response.status_code == 403


def test_admin_get_blocked_album_by_id(client):
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


def test_listener_get_all_albums_returns_only_not_blocked_albums(client):
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


def test_admin_get_all_albums_returns_blocked_and_not_blocked_albums(client):
    post_user(client, uid="artist_id", user_name="artist_name")

    post_album(client, uid="artist_id", name="not_blocked_album", blocked=False)
    post_album(client, uid="artist_id", name="blocked_album", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/",
        headers={"role": "admin", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_admin_get_album_by_id_indicates_if_album_is_blocked(client):
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


def test_artist_get_my_albums_returns_blocked_albums(client):
    post_user(client, uid="artist_id", user_name="artist_name")

    post_album(client, uid="artist_id", name="not_blocked_album", blocked=False)
    post_album(client, uid="artist_id", name="blocked_album", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/my_albums/",
        headers={"uid": "artist_id", "role": "artist", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_album_by_id_invalid_role(client):
    post_user(client, uid="artist_id", user_name="artist_name")

    album_id = post_album(client, uid="artist_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"role": "an_invalid_role", "api_key": "key"},
    )

    assert response.status_code == 422


def test_get_albums_invalid_role(client):
    post_user(client, uid="artist_id", user_name="artist_name")
    post_album(client, uid="artist_id", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/",
        headers={"role": "an_invalid_role", "api_key": "key"},
    )

    assert response.status_code == 422


def test_listener_get_album_by_id_with_blocked_songs_should_retrieve_not_blocked_songs(
    client,
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
    block_song(client, id=song_id_1)

    album_id = album_id.json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}",
        headers={"role": "listener", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()["songs"]) == 1
    assert response.json()["songs"][0]["name"] == "not_blocked_song"


def test_listener_get_album_by_id_with_blocked_songs_should_not_remove_song(client):
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

    response_get_song = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id_1}",
        headers={"role": "admin", "api_key": "key"},
    )
    assert response_get_song.status_code == 200


def test_user_cannot_modify_blocked_status_of_playlist(client):
    post_user(client, uid="artist_id", user_name="artist_name")
    playlist_id = post_playlist(client, uid="artist_id").json()["id"]

    response = client.put(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        data={"blocked": True},
        headers={"uid": "artist_id", "role": "listener", "api_key": "key"},
    )
    assert response.status_code == 403


def test_admin_can_modify_blocked_status_of_playlist(client):
    post_user(client, uid="admin_id", user_name="admin_name")
    post_user(client, uid="artist_id", user_name="artist_name")
    playlist_id = post_playlist(client, uid="artist_id").json()["id"]

    response_put = client.put(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        data={"blocked": True},
        headers={"uid": "admin_id", "role": "admin", "api_key": "key"},
    )
    assert response_put.status_code == 200


def test_listener_get_not_blocked_playlist_by_id(client):
    post_user(client, uid="artist_id", user_name="artist_name")

    playlist_id = post_playlist(client, uid="artist_id", blocked=False).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"role": "listener", "api_key": "key"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "playlist_name"


def test_listener_get_blocked_playlist_by_id_should_fail(client):
    post_user(client, uid="artist_id", user_name="artist_name")

    playlist_id = post_playlist(client, uid="artist_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"role": "listener", "api_key": "key"},
    )

    assert response.status_code == 403


def test_admin_get_blocked_playlist_by_id(client):
    post_user(client, uid="artist_id", user_name="artist_name")

    playlist_id = post_playlist(client, uid="artist_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"role": "admin", "api_key": "key"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "playlist_name"


def test_listener_get_all_playlists_returns_only_not_blocked_playlists(client):
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


def test_admin_get_all_playlists_returns_blocked_and_not_blocked_playlists(client):
    post_user(client, uid="artist_id", user_name="artist_name")

    post_playlist(client, uid="artist_id", blocked=False)
    post_playlist(client, uid="artist_id", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/",
        headers={"role": "admin", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_admin_get_playlist_by_id_indicates_if_playlist_is_blocked(client):
    post_user(client, uid="admin_id", user_name="admin_name")

    playlist_id = post_playlist(client, uid="admin_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"role": "admin", "api_key": "key"},
    )

    assert response.status_code == 200
    assert response.json()["blocked"] is True


def test_artist_get_my_playlists_returns_blocked_playlists(client):
    post_user(client, uid="artist_id", user_name="artist_name")

    post_playlist(client, uid="artist_id", blocked=False)
    post_playlist(client, uid="artist_id", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/my_playlists/",
        headers={"uid": "artist_id", "role": "artist", "api_key": "key"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_playlist_by_id_invalid_role(client):
    post_user(client, uid="artist_id", user_name="artist_name")

    playlist_id = post_playlist(client, uid="artist_id", blocked=True).json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"role": "an_invalid_role", "api_key": "key"},
    )

    assert response.status_code == 422


def test_get_playlists_invalid_role(client):
    post_user(client, uid="artist_id", user_name="artist_name")
    post_playlist(client, uid="artist_id", blocked=True)

    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/",
        headers={"role": "an_invalid_role", "api_key": "key"},
    )

    assert response.status_code == 422


def test_listener_get_playlist_by_id_with_blocked_songs_should_retrieve_not_blocked_songs(
    client,
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


def test_listener_get_playlist_by_id_with_blocked_songs_should_not_remove_song(client):
    # This is a white box test

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
        headers={"role": "admin", "api_key": "key"},
    )
    assert response_get_song.status_code == 200
