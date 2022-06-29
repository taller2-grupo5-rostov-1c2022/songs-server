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
    utils.post_users(client, "artist_id", "admin_id")
    song_id = post_song(client, uid="artist_id")

    response_put = utils.put_song(client, song_id, {"blocked": True}, role="artist")
    assert response_put.status_code == 403

    response_get = utils.get_song(client, song_id, uid="admin_id", role="admin")
    song = response_get.json()

    assert response_get.status_code == 200
    assert song["blocked"] is False


def test_admin_can_modify_blocked_status_of_song(client, custom_requests_mock):
    utils.post_users(client, "artist_id", "admin_id")
    song_id = post_song(client, uid="artist_id")

    response_put = utils.put_song(
        client, song_id, {"blocked": True}, uid="admin_id", role="admin"
    )
    assert response_put.status_code == 200


def test_listener_get_not_blocked_song_by_id(client, custom_requests_mock):
    utils.post_users(client, "listener_id", "artist_id")

    song_id = post_song(client, uid="artist_id")

    response = utils.get_song(client, song_id, uid="listener_id", role="listener")

    assert response.status_code == 200


def test_listener_get_blocked_song_by_id_should_fail(client, custom_requests_mock):
    utils.post_users(client, "listener_id", "artist_id")

    song_id = post_song(client, uid="artist_id", blocked=True)

    response = utils.get_song(client, song_id, uid="listener_id", role="listener")

    assert response.status_code == 404


def test_artist_get_blocked_song_by_id_should_fail(client, custom_requests_mock):
    utils.post_users(client, "artist_id", "another_artist_id")
    song_id = post_song(client, uid="artist_id", blocked=True)

    response = utils.get_song(client, song_id, uid="artist_id", role="artist")

    assert response.status_code == 404


def test_user_without_role_get_blocked_song_by_id_should_fail(
    client, custom_requests_mock
):
    utils.post_users(client, "artist_id", "user_without_role_id")
    song_id = post_song(client, uid="artist_id", blocked=True)

    response = utils.get_song(client, song_id, uid="user_without_role_id", role=None)

    assert response.status_code == 404


def test_admin_get_blocked_song_by_id(client, custom_requests_mock):
    utils.post_users(client, "admin_id", "artist_id")
    song_id = post_song(client, uid="artist_id", blocked=True)

    response = utils.get_song(client, song_id, uid="admin_id", role="admin")

    assert response.status_code == 200


def test_listener_get_all_songs_returns_only_not_blocked_songs(
    client, custom_requests_mock
):
    utils.post_users(client, "artist_id", "listener_id")

    post_song(client, uid="artist_id", blocked=False)
    post_song(client, uid="artist_id", blocked=True)

    response = utils.search_songs(client, uid="listener_id", role="listener")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 1
    assert songs[0]["blocked"] is False


def test_admin_get_all_songs_returns_blocked_and_not_blocked_songs(
    client, custom_requests_mock
):
    utils.post_users(client, "admin_id", "artist_id")
    post_song(client, uid="artist_id", name="not_blocked_song", blocked=False)
    post_song(client, uid="artist_id", name="blocked_song", blocked=True)

    response = utils.search_songs(client, uid="admin_id", role="admin")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 2


def test_artist_get_my_songs_returns_blocked_songs(client, custom_requests_mock):
    post_user(client, "artist_id")

    post_song(client, name="not_blocked_song", blocked=False)
    post_song(client, name="blocked_song", blocked=True)

    response = utils.get_my_songs(client, uid="artist_id", role="artist")
    songs = response.json()

    assert response.status_code == 200
    assert len(songs) == 2


def test_get_song_by_id_invalid_role(client, custom_requests_mock):
    post_user(client, "artist_id")

    song_id = post_song(client, uid="artist_id", blocked=True)
    response = utils.get_song(client, song_id, uid="artist_id", role="invalid")

    assert response.status_code == 422


def test_get_songs_invalid_role(client, custom_requests_mock):
    post_song(client, blocked=True)

    response = utils.search_songs(client, role="invalid")

    assert response.status_code == 422


def test_user_cannot_modify_blocked_status_of_album(client, custom_requests_mock):
    post_user(client, "artist_id")
    album_id = post_album(client, uid="artist_id")

    response_put = utils.put_album(
        client, album_id, {"blocked": True}, uid="artist_id", role="artist"
    )

    assert response_put.status_code == 403


def test_admin_can_modify_blocked_status_of_album(client, custom_requests_mock):
    post_user(client, "admin_id")
    post_user(client, "artist_id")
    album_id = post_album(client, uid="artist_id")

    response_put = utils.put_album(
        client, album_id, {"blocked": True}, uid="admin_id", role="admin"
    )

    assert response_put.status_code == 200


def test_listener_get_not_blocked_album_by_id(client, custom_requests_mock):
    utils.post_users(client, "artist_id", "listener_id")

    album_id = post_album(client, name="my_album_name", uid="artist_id", blocked=False)

    response = utils.get_album(client, album_id, uid="listener_id", role="listener")

    assert response.status_code == 200
    assert response.json()["name"] == "my_album_name"


def test_listener_get_blocked_album_by_id_should_fail(client, custom_requests_mock):
    utils.post_users(client, "artist_id", "listener_id")

    album_id = post_album(client, name="my_album_name", uid="artist_id", blocked=True)

    response = utils.get_album(client, album_id, uid="listener_id", role="listener")

    assert response.status_code == 404


def test_admin_get_blocked_album_by_id(client, custom_requests_mock):
    utils.post_users(client, "artist_id", "admin_id")

    album_id = post_album(client, name="my_album_name", uid="artist_id", blocked=True)

    response = utils.get_album(client, album_id, uid="admin_id", role="admin")
    album = response.json()

    assert response.status_code == 200
    assert album["name"] == "my_album_name"
    assert album["blocked"] is True


def test_listener_get_all_albums_returns_only_not_blocked_albums(
    client, custom_requests_mock
):
    utils.post_users(client, "artist_id", "listener_id")

    post_album(client, uid="artist_id", blocked=False)
    post_album(client, uid="artist_id", blocked=True)

    response = utils.search_albums(client, uid="listener_id", role="listener")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 1
    assert albums[0]["blocked"] is False


def test_admin_get_all_albums_returns_blocked_and_not_blocked_albums(
    client, custom_requests_mock
):
    utils.post_users(client, "artist_id", "admin_id")

    post_album(client, uid="artist_id", blocked=False)
    post_album(client, uid="artist_id", blocked=True)

    response = utils.search_albums(client, uid="admin_id", role="admin")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 2
    assert albums[0]["blocked"] is False
    assert albums[1]["blocked"] is True


def test_artist_get_my_albums_returns_blocked_albums(client, custom_requests_mock):
    post_user(client, "artist_id")

    post_album(client, uid="artist_id", blocked=False)
    post_album(client, uid="artist_id", blocked=True)

    response = utils.get_my_albums(client, uid="artist_id", role="artist")
    albums = response.json()

    assert response.status_code == 200
    assert len(albums) == 2
    assert albums[0]["blocked"] is False
    assert albums[1]["blocked"] is True


def test_get_album_by_id_invalid_role(client, custom_requests_mock):
    post_user(client, "artist_id")

    album_id = post_album(client, uid="artist_id", blocked=True)

    response = utils.get_album(client, album_id, uid="artist_id", role="invalid")

    assert response.status_code == 422


def test_get_albums_invalid_role(client, custom_requests_mock):
    post_user(client, "artist_id")
    post_album(client, uid="artist_id", blocked=True)

    response = utils.search_albums(client, role="invalid")

    assert response.status_code == 422


def test_user_cannot_modify_blocked_status_of_playlist(client, custom_requests_mock):
    post_user(client, "artist_id")
    playlist_id = post_playlist(client, uid="artist_id")

    response_put = utils.put_playlist(
        client, playlist_id, {"blocked": True}, uid="artist_id", role="artist"
    )

    assert response_put.status_code == 403


def test_admin_can_modify_blocked_status_of_playlist(client, custom_requests_mock):
    utils.post_users(client, "admin_id", "artist_id")
    playlist_id = post_playlist(client, uid="artist_id")

    response_put = utils.put_playlist(
        client, playlist_id, {"blocked": True}, uid="admin_id", role="admin"
    )

    assert response_put.status_code == 200


def test_listener_get_not_blocked_playlist_by_id(client, custom_requests_mock):
    utils.post_users(client, "artist_id", "listener_id")

    playlist_id = post_playlist(client, uid="artist_id", blocked=False)

    response = utils.get_playlist(
        client, playlist_id, uid="listener_id", role="listener"
    )
    playlist = response.json()

    assert response.status_code == 200
    assert playlist["blocked"] is False


def test_listener_get_blocked_playlist_by_id_should_fail(client, custom_requests_mock):
    utils.post_users(client, "artist_id", "listener_id")

    playlist_id = post_playlist(client, uid="artist_id", blocked=True)

    response = utils.get_playlist(
        client, playlist_id, uid="listener_id", role="listener"
    )

    assert response.status_code == 404


def test_admin_get_blocked_playlist_by_id(client, custom_requests_mock):
    utils.post_users(client, "artist_id", "admin_id")

    playlist_id = post_playlist(client, uid="artist_id", blocked=True)

    response = utils.get_playlist(client, playlist_id, uid="admin_id", role="admin")
    playlist = response.json()

    assert response.status_code == 200
    assert playlist["blocked"] is True


def test_listener_get_all_playlists_returns_only_not_blocked_playlists(
    client, custom_requests_mock
):
    utils.post_users(client, "artist_id", "listener_id")

    post_playlist(client, uid="artist_id", blocked=False)
    post_playlist(client, uid="artist_id", blocked=True)

    response = utils.search_playlists(client, uid="listener_id", role="listener")
    playlists = response.json()

    assert response.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["blocked"] is False


def test_admin_get_all_playlists_returns_blocked_and_not_blocked_playlists(
    client, custom_requests_mock
):
    utils.post_users(client, "artist_id", "admin_id")

    post_playlist(client, uid="artist_id", blocked=False)
    post_playlist(client, uid="artist_id", blocked=True)

    response = utils.search_playlists(client, uid="admin_id", role="admin")
    playlists = response.json()

    assert response.status_code == 200
    assert len(playlists) == 2


def test_artist_get_my_playlists_returns_blocked_playlists(
    client, custom_requests_mock
):
    post_user(client, "artist_id")

    post_playlist(client, uid="artist_id", blocked=False)
    post_playlist(client, uid="artist_id", blocked=True)

    response = utils.get_my_playlists(client, uid="artist_id", role="artist")
    playlists = response.json()

    assert response.status_code == 200
    assert len(playlists) == 2


def test_get_playlist_by_id_invalid_role(client, custom_requests_mock):
    post_user(client, "artist_id")

    playlist_id = post_playlist(client, uid="artist_id", blocked=True)
    response = utils.get_playlist(client, playlist_id, uid="artist_id", role="invalid")

    assert response.status_code == 422


def test_get_playlists_invalid_role(client, custom_requests_mock):
    post_user(client, "artist_id")
    post_playlist(client, uid="artist_id", blocked=True)

    response = utils.search_playlists(client, role="invalid")

    assert response.status_code == 422


def test_listener_edit_album_with_blocked_song_does_not_modify_blocked_song(
    client, custom_requests_mock
):
    utils.post_users(client, "artist_id", "admin_id")

    song_id = post_song(client, uid="artist_id", name="blocked_song", blocked=False)
    album_id = post_album(client, "artist_id", songs_ids=[song_id])
    block_song(client, song_id)

    response_put = utils.put_album(
        client,
        album_id,
        {"songs_ids": "[]", "name": "updated_test_album"},
        uid="artist_id",
        role="artist",
    )
    assert response_put.status_code == 200

    response_get = utils.get_album(client, album_id, uid="admin_id", role="admin")
    album = response_get.json()

    assert response_get.status_code == 200
    assert len(album["songs"]) == 1
    assert album["name"] == "updated_test_album"
    assert album["songs"][0]["blocked"] is True


def test_admin_edit_album_can_modify_blocked_song(client, custom_requests_mock):
    utils.post_users(client, "admin_id", "another_admin_id")

    song_id = post_song(client, uid="admin_id", name="blocked_song", blocked=False)
    album_id = post_album(client, "admin_id", songs_ids=[song_id])
    block_song(client, song_id)

    response_put = utils.put_album(
        client,
        album_id,
        {"songs_ids": "[]", "name": "updated_test_album"},
        uid="admin_id",
        role="admin",
    )
    assert response_put.status_code == 200

    response_get = utils.get_album(
        client, album_id, uid="another_admin_id", role="admin"
    )
    album = response_get.json()

    assert response_get.status_code == 200
    assert len(album["songs"]) == 0


def test_listener_edit_playlist_with_blocked_song_does_not_modify_blocked_song(
    client, custom_requests_mock
):
    utils.post_users(client, "artist_id", "admin_id")

    song_id = post_song(client, uid="artist_id", name="blocked_song", blocked=False)

    playlist_id = post_playlist(client, "artist_id", songs_ids=[song_id])
    block_song(client, song_id)

    response_put = utils.put_playlist(
        client,
        playlist_id,
        {"songs_ids": "[]", "name": "updated_test_playlist"},
        uid="artist_id",
        role="artist",
    )
    assert response_put.status_code == 200

    response_get = utils.get_playlist(client, playlist_id, uid="admin_id", role="admin")
    playlist = response_get.json()

    assert response_get.status_code == 200
    assert playlist["name"] == "updated_test_playlist"
    assert len(playlist["songs"]) == 1
    assert playlist["songs"][0]["blocked"] is True


def test_listener_remove_blocked_song_from_playlist_does_not_remove_it(
    client, custom_requests_mock
):
    utils.post_users(client, "listener_id", "artist_id", "admin_id")

    song_id = post_song(client, uid="artist_id", blocked=False)
    playlist_id = post_playlist(client, "listener_id", songs_ids=[song_id])
    block_song(client, song_id)

    response_delete = utils.remove_playlist_song(
        client, playlist_id, song_id, uid="listener_id", role="artist"
    )

    assert response_delete.status_code == 404


def test_admin_remove_blocked_song_from_playlist_removes_it(
    client, custom_requests_mock
):
    utils.post_users(client, "admin_id", "artist_id", "listener_id")

    song_id = post_song(client, uid="artist_id", blocked=False)

    playlist_id = post_playlist(client, "listener_id", songs_ids=[song_id])
    block_song(client, song_id)

    response_delete = utils.remove_playlist_song(
        client, playlist_id, song_id, uid="admin_id", role="admin"
    )
    assert response_delete.status_code == 200

    response_get = utils.get_playlist(
        client, playlist_id, uid="listener_id", role="artist"
    )
    playlist = response_get.json()

    assert response_get.status_code == 200
    assert len(playlist["songs"]) == 0
