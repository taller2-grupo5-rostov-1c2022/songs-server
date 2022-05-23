from tests import utils
from tests.utils import API_VERSION_PREFIX


def test_get_favorite_songs_with_zero_favorite_songs(client):
    utils.post_user(client, "user_id", "user_name")
    response_get = client.get(
        f"{API_VERSION_PREFIX}/users/user_id/favorites/songs",
        headers={
            "api_key": "key",
            "uid": "user_id",
        },
    )
    assert response_get.status_code == 200
    assert response_get.json() == []


def test_get_favorite_songs_with_one_favorite_songs(client):
    utils.post_user(client, "user_id", "user_name")
    song_id = utils.post_song(client, uid="user_id").json()["id"]
    response_post = utils.add_song_to_favorites(client, uid="user_id", song_id=song_id)
    assert response_post.status_code == 200

    response_get = utils.get_favorite_songs(client, uid="user_id")

    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_name"


def test_get_favorite_songs_with_two_favorite_songs(client):
    utils.post_user(client, "user_id", "user_name")
    song_id_1 = utils.post_song(client, name="first_song", uid="user_id").json()["id"]
    song_id_2 = utils.post_song(client, name="second_song", uid="user_id").json()["id"]
    response_post = utils.add_song_to_favorites(
        client, uid="user_id", song_id=song_id_1
    )
    assert response_post.status_code == 200
    response_post = utils.add_song_to_favorites(
        client, uid="user_id", song_id=song_id_2
    )
    assert response_post.status_code == 200

    response_get = utils.get_favorite_songs(client, uid="user_id")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 2
    assert songs[0]["name"] == "first_song"
    assert songs[1]["name"] == "second_song"


def test_get_favorite_songs_only_returns_favorite_songs(client):
    utils.post_user(client, "user_id", "user_name")
    song_id_1 = utils.post_song(client, name="first_song", uid="user_id").json()["id"]
    utils.post_song(client, name="second_song", uid="user_id")

    utils.add_song_to_favorites(client, uid="user_id", song_id=song_id_1)
    response_get = utils.get_favorite_songs(client, uid="user_id")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "first_song"


def test_get_favorite_songs_with_blocked_song(client):
    utils.post_user(client, "user_id", "user_name")
    song_id_1 = utils.post_song(client, name="first_song", uid="user_id").json()["id"]
    song_id_2 = utils.post_song(client, name="second_song", uid="user_id").json()["id"]
    response_post = utils.add_song_to_favorites(
        client, uid="user_id", song_id=song_id_1
    )
    assert response_post.status_code == 200
    response_post = utils.add_song_to_favorites(
        client, uid="user_id", song_id=song_id_2
    )
    assert response_post.status_code == 200
    utils.block_song(client, song_id=song_id_1)

    response_get = utils.get_favorite_songs(client, uid="user_id")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "second_song"


def test_remove_song_from_favorites(client):
    utils.post_user(client, "user_id", "user_name")
    song_id = utils.post_song(client, uid="user_id").json()["id"]
    response_post = utils.add_song_to_favorites(client, uid="user_id", song_id=song_id)
    assert response_post.status_code == 200

    response_get = utils.get_favorite_songs(client, uid="user_id")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["name"] == "song_name"

    response_delete = utils.delete_song_from_favorites(
        client, uid="user_id", song_id=song_id
    )
    assert response_delete.status_code == 200

    response_get = utils.get_favorite_songs(client, uid="user_id")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 0


def test_remove_song_from_favorites_does_not_delete_song(client):
    utils.post_user(client, "user_id", "user_name")
    song_id = utils.post_song(client, uid="user_id").json()["id"]
    utils.add_song_to_favorites(client, uid="user_id", song_id=song_id)

    utils.delete_song_from_favorites(client, uid="user_id", song_id=song_id)

    response_get = utils.get_song(client, song_id=song_id)
    song = response_get.json()

    assert response_get.status_code == 200
    assert song["name"] == "song_name"


def test_remove_song_from_favorites_removes_only_expected_song(client):
    utils.post_user(client, "user_id", "user_name")
    song_id_1 = utils.post_song(client, name="first_song", uid="user_id").json()["id"]
    song_id_2 = utils.post_song(client, name="second_song", uid="user_id").json()["id"]
    utils.add_song_to_favorites(client, uid="user_id", song_id=song_id_1)
    utils.add_song_to_favorites(client, uid="user_id", song_id=song_id_2)

    response_delete = utils.delete_song_from_favorites(
        client, uid="user_id", song_id=song_id_1
    )
    assert response_delete.status_code == 200

    response_get = utils.get_favorite_songs(client, uid="user_id")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["id"] == song_id_2
    assert songs[0]["name"] == "second_song"


def test_remove_song_from_favorites_song_that_is_not_in_favorites(client):
    utils.post_user(client, "user_id", "user_name")
    song_id_1 = utils.post_song(client, name="first_song", uid="user_id").json()["id"]
    song_id_2 = utils.post_song(client, name="second_song", uid="user_id").json()["id"]
    utils.add_song_to_favorites(client, uid="user_id", song_id=song_id_1)

    response_delete = utils.delete_song_from_favorites(
        client, uid="user_id", song_id=song_id_2
    )
    assert response_delete.status_code == 404

    response_get = utils.get_favorite_songs(client, uid="user_id")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["id"] == song_id_1
    assert songs[0]["name"] == "first_song"


def test_user_cann_add_to_favorites_songs_of_another_user(client):
    utils.post_user(client, "creator_id", "creator_name")
    utils.post_user(client, "listener_id", "listener_name")
    song_id = utils.post_song(client, name="song_by_creator", uid="creator_id").json()[
        "id"
    ]

    utils.add_song_to_favorites(client, uid="listener_id", song_id=song_id)
    response_get = utils.get_favorite_songs(client, uid="listener_id")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["id"] == song_id
    assert songs[0]["name"] == "song_by_creator"


def test_admin_can_add_song_to_favorites_even_if_blocked(client):
    utils.post_user(client, "user_id", "user_name")
    song_id = utils.post_song(client, name="song_name", uid="user_id").json()["id"]

    utils.add_song_to_favorites(client, uid="user_id", song_id=song_id)

    utils.block_song(client, song_id=song_id)

    response_get = utils.get_favorite_songs(client, uid="user_id", role="admin")
    songs = response_get.json()

    assert response_get.status_code == 200
    assert len(songs) == 1
    assert songs[0]["id"] == song_id
    assert songs[0]["name"] == "song_name"


def test_get_favorite_albums_with_zero_favorite_albums(client):
    utils.post_user(client, "user_id", "user_name")
    response_get = utils.get_favorite_albums(client, uid="user_id")
    albums = response_get.json()

    assert response_get.status_code == 200
    assert len(albums) == 0


def test_get_favorite_albums_with_one_favorite_album(client):
    utils.post_user(client, "user_id", "user_name")
    album_id = utils.post_album(client, name="album_name", uid="user_id").json()["id"]
    response_post = utils.add_album_to_favorites(
        client, uid="user_id", album_id=album_id
    )
    assert response_post.status_code == 200

    response_get = utils.get_favorite_albums(client, uid="user_id")
    albums = response_get.json()

    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_name"
    assert albums[0]["cover"].startswith("http")
    assert albums[0]["score"] == 0
    assert albums[0]["scores_amount"] == 0


def test_get_favorite_albums_with_one_favorite_album_with_one_song(client):
    utils.post_user(client, "user_id", "user_name")
    song_id = utils.post_song(client, name="song_name", uid="user_id").json()["id"]
    album_id = utils.post_album(
        client, name="album_name", uid="user_id", songs_ids=[song_id]
    ).json()["id"]

    response_post = utils.add_album_to_favorites(
        client, uid="user_id", album_id=album_id
    )
    assert response_post.status_code == 200

    response_get = utils.get_favorite_albums(client, uid="user_id")
    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_name"
    assert len(albums[0]["songs"]) == 1
    assert albums[0]["songs"][0]["name"] == "song_name"


def test_get_favorite_albums_with_one_favorite_album_with_blocked_song_returns_empty_album(
    client,
):
    utils.post_user(client, "user_id", "user_name")
    song_id = utils.post_song(client, name="song_name", uid="user_id").json()["id"]
    album_id = utils.post_album(
        client, name="album_name", uid="user_id", songs_ids=[song_id]
    ).json()["id"]

    response_post = utils.add_album_to_favorites(
        client, uid="user_id", album_id=album_id
    )
    assert response_post.status_code == 200

    utils.block_song(client, song_id=song_id)

    response_get = utils.get_favorite_albums(client, uid="user_id")
    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_name"
    assert len(albums[0]["songs"]) == 0


def test_get_favorite_albums_with_blocked_and_non_blocked_song_returns_album_with_non_blocked_song(
    client,
):
    utils.post_user(client, "user_id", "user_name")
    song_id_1 = utils.post_song(client, name="song_1", uid="user_id").json()["id"]
    song_id_2 = utils.post_song(client, name="song_2", uid="user_id").json()["id"]
    album_id = utils.post_album(
        client, name="album_name", uid="user_id", songs_ids=[song_id_1, song_id_2]
    ).json()["id"]

    response_post = utils.add_album_to_favorites(
        client, uid="user_id", album_id=album_id
    )
    assert response_post.status_code == 200

    utils.block_song(client, song_id=song_id_1)

    response_get = utils.get_favorite_albums(client, uid="user_id")
    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert len(albums[0]["songs"]) == 1
    assert albums[0]["songs"][0]["name"] == "song_2"


def test_get_favorite_albums_with_two_albums_returns_only_favorite_albums(client):
    utils.post_user(client, "user_id", "user_name")
    album_id_1 = utils.post_album(
        client, name="album_1", uid="user_id", songs_ids=[]
    ).json()["id"]
    utils.post_album(client, name="album_2", uid="user_id", songs_ids=[])

    response_post = utils.add_album_to_favorites(
        client, uid="user_id", album_id=album_id_1
    )
    assert response_post.status_code == 200

    response_get = utils.get_favorite_albums(client, uid="user_id")
    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_1"


def test_get_favorite_albums_with_two_albums_returns_only_favorite_albums_with_one_song(
    client,
):
    utils.post_user(client, "user_id", "user_name")
    song_id = utils.post_song(client, name="song_name", uid="user_id").json()["id"]
    album_id_1 = utils.post_album(
        client, name="album_1", uid="user_id", songs_ids=[song_id]
    ).json()["id"]
    utils.post_album(client, name="album_2", uid="user_id", songs_ids=[])

    response_post = utils.add_album_to_favorites(
        client, uid="user_id", album_id=album_id_1
    )
    assert response_post.status_code == 200

    response_get = utils.get_favorite_albums(client, uid="user_id")
    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert len(albums[0]["songs"]) == 1
    assert albums[0]["songs"][0]["name"] == "song_name"


def test_get_favorite_albums_does_not_return_blocked_albums(client):
    utils.post_user(client, "user_id", "user_name")
    song_id = utils.post_song(client, name="song_name", uid="user_id").json()["id"]
    album_id_1 = utils.post_album(
        client, name="album_1", uid="user_id", songs_ids=[song_id]
    ).json()["id"]
    album_id_2 = utils.post_album(client, name="album_2", uid="user_id").json()["id"]

    response_post = utils.add_album_to_favorites(
        client, uid="user_id", album_id=album_id_1
    )
    assert response_post.status_code == 200

    response_post = utils.add_album_to_favorites(
        client, uid="user_id", album_id=album_id_2
    )
    assert response_post.status_code == 200

    utils.block_album(client, id=album_id_1)

    response_get = utils.get_favorite_albums(client, uid="user_id")
    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 1
    assert albums[0]["name"] == "album_2"


def test_remove_album_from_favorites(client):
    utils.post_user(client, "user_id", "user_name")
    album_id = utils.post_album(
        client, name="album_name", uid="user_id", songs_ids=[]
    ).json()["id"]

    utils.add_album_to_favorites(client, uid="user_id", album_id=album_id)

    response_delete = utils.remove_album_from_favorites(
        client, uid="user_id", album_id=album_id
    )
    assert response_delete.status_code == 200

    response_get = utils.get_favorite_albums(client, uid="user_id")
    albums = response_get.json()
    assert response_get.status_code == 200
    assert len(albums) == 0


def test_remove_album_from_favorites_album_not_in_favorites(client):
    utils.post_user(client, "user_id", "user_name")
    album_id = utils.post_album(
        client, name="album_name", uid="user_id", songs_ids=[]
    ).json()["id"]

    response_delete = utils.remove_album_from_favorites(
        client, uid="user_id", album_id=album_id
    )
    assert response_delete.status_code == 404


def test_get_favorite_playlists_with_zero_playlists(client):
    utils.post_user(client, "user_id", "user_name")
    response_get = utils.get_favorite_playlists(client, uid="user_id")
    assert response_get.status_code == 200
    assert len(response_get.json()) == 0


def test_get_favorite_playlists_with_one_playlist(client):
    utils.post_user(client, "user_id", "user_name")
    playlist_id = utils.post_playlist(
        client, playlist_name="playlist_name", uid="user_id"
    ).json()["id"]

    response_post = utils.add_playlist_to_favorites(
        client, uid="user_id", playlist_id=playlist_id
    )
    assert response_post.status_code == 200

    response_get = utils.get_favorite_playlists(client, uid="user_id")
    playlists = response_get.json()
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_name"


def test_get_favorite_playlists_returns_only_favorite_playlists(client):
    utils.post_user(client, "user_id", "user_name")
    playlist_id_1 = utils.post_playlist(
        client, playlist_name="playlist_name_1", uid="user_id"
    ).json()["id"]
    utils.post_playlist(client, playlist_name="playlist_name_2", uid="user_id")

    utils.add_playlist_to_favorites(client, uid="user_id", playlist_id=playlist_id_1)

    response_get = utils.get_favorite_playlists(client, uid="user_id")
    playlists = response_get.json()
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_name_1"


def test_cannot_add_blocked_playlist_to_favorites_from_another_user(client):
    utils.post_user(client, "user_id", "user_name")
    utils.post_user(client, "user_id_2", "user_name_2")
    playlist_id = utils.post_playlist(
        client, playlist_name="playlist_name", uid="user_id_2"
    ).json()["id"]

    utils.block_playlist(client, playlist_id=playlist_id)

    response_post = utils.add_playlist_to_favorites(
        client, uid="user_id", playlist_id=playlist_id
    )
    assert response_post.status_code == 404


def test_get_favorite_playlists_does_not_return_blocked_playlists(client):
    utils.post_user(client, "user_id", "user_name")
    playlist_id_1 = utils.post_playlist(
        client, playlist_name="playlist_name_1", uid="user_id"
    ).json()["id"]
    playlist_id_2 = utils.post_playlist(
        client, playlist_name="playlist_name_2", uid="user_id"
    ).json()["id"]

    utils.add_playlist_to_favorites(client, uid="user_id", playlist_id=playlist_id_1)
    utils.add_playlist_to_favorites(client, uid="user_id", playlist_id=playlist_id_2)

    utils.block_playlist(client, playlist_id=playlist_id_1)

    response_get = utils.get_favorite_playlists(client, uid="user_id")
    playlists = response_get.json()
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_name_2"


def test_admin_can_add_playlist_to_favorites_even_if_blocked(client):
    utils.post_user(client, "admin_id", "admin_name")
    utils.post_user(client, "creator_id", "creator_name")
    playlist_id = utils.post_playlist(
        client, playlist_name="playlist_name", uid="creator_id"
    ).json()["id"]

    utils.block_playlist(client, playlist_id=playlist_id)

    response_post = utils.add_playlist_to_favorites(
        client, uid="admin_id", playlist_id=playlist_id, role="admin"
    )
    assert response_post.status_code == 200

    response_get = utils.get_favorite_playlists(client, uid="admin_id", role="admin")
    playlists = response_get.json()
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_name"


"""
def test_get_favorite_playlists_return_playlist_without_blocked_songs(client):
    utils.post_user(client, "creator_id", "creator_name")
    utils.post_user(client, "user_id", "user_name")
    song_id = utils.post_song(client, uid="creator_id", name="song_name").json()["id"]

    playlist_id = utils.post_playlist(
        client, playlist_name="playlist_name", uid="creator_id", songs_ids=[song_id]
    )
    playlist_id = playlist_id.json()["id"]

    utils.add_playlist_to_favorites(client, uid="user_id", playlist_id=playlist_id)

    utils.block_song(client, song_id=song_id)

    response_get = utils.get_favorite_playlists(client, uid="user_id")
    playlists = response_get.json()
    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_name"
    assert len(playlists[0]["songs"]) == 0
"""
