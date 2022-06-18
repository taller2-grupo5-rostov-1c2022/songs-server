from tests import utils
from tests.utils import (
    API_VERSION_PREFIX,
    post_song,
    post_user,
    post_playlist,
    wrap_post_playlist,
)


def test_get_playlist_by_id_should_return_404_if_playlist_not_found(
    client, custom_requests_mock, drop_tables
):
    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/1", headers={"api_key": "key"}
    )

    assert response.status_code == 404


def test_get_playlist_by_id_should_return_403_if_not_authorized(
    client, custom_requests_mock, drop_tables
):
    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/1", headers={"api_key": "wrong_key"}
    )

    assert response.status_code == 403


def test_get_playlist_should_return_empty_response(
    client, custom_requests_mock, drop_tables
):
    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/", headers={"api_key": "key"}
    )
    assert response.status_code == 200
    assert response.json() == []


def test_post_playlist_should_return_its_id(client, custom_requests_mock, drop_tables):
    response = wrap_post_playlist(client)

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_playlist_by_id(client, custom_requests_mock, drop_tables):
    response_post = wrap_post_playlist(client)

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/{response_post.json()['id']}",
        headers={"api_key": "key"},
    )

    playlist = response_get.json()

    assert response_get.status_code == 200
    assert playlist["id"] == 1
    assert playlist["name"] == "playlist_name"
    assert len(playlist["colabs"]) == 1
    assert playlist["colabs"][0]["name"] == "Fernandito"
    assert playlist["creator_id"] == "user_playlist_owner"
    assert playlist["description"] == "playlist_description"
    assert playlist["songs"][0]["name"] == "song_for_playlist1"
    assert playlist["songs"][1]["name"] == "song_for_playlist2"


def test_get_all_playlists_with_no_specific_uid(
    client, custom_requests_mock, drop_tables
):

    # Create two playlists
    wrap_post_playlist(client)
    res_1 = post_song(client, uid="user_playlist_owner", name="song_for_playlist1")
    res_2 = post_song(client, uid="user_playlist_owner", name="song_for_playlist2")
    colabs_id = ["user_playlist_colab"]
    songs_id = [res_1.json()["id"], res_2.json()["id"]]
    post_playlist(
        client,
        uid="user_playlist_owner",
        playlist_name="playlist_name",
        description="playlist_description",
        colabs_ids=colabs_id,
        songs_ids=songs_id,
    )

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/", headers={"api_key": "key"}
    )

    playlists = response_get.json()

    assert response_get.status_code == 200
    assert len(playlists) == 2


def test_get_playlist_from_uid(client, custom_requests_mock, drop_tables):

    # Two users
    post_user(client, uid="user_playlist_owner", user_name="Ricardito")
    post_user(client, uid="user_playlist_colab", user_name="Fernandito")

    # Two songs
    res_1 = post_song(client, uid="user_playlist_owner", name="song_for_playlist1")
    res_2 = post_song(client, uid="user_playlist_owner", name="song_for_playlist2")
    colabs_id_playlist_1 = ["user_playlist_colab"]
    colabs_id_playlist_2 = []
    songs_id = [res_1.json()["id"], res_2.json()["id"]]

    # Two playlists
    post_playlist(
        client,
        uid="user_playlist_owner",
        playlist_name="playlist_name1",
        description="playlist_description1",
        colabs_ids=colabs_id_playlist_1,
        songs_ids=songs_id,
    )
    post_playlist(
        client,
        uid="user_playlist_colab",
        playlist_name="playlist_name2",
        description="playlist_description2",
        colabs_ids=colabs_id_playlist_2,
        songs_ids=songs_id,
    )

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/?colab=user_playlist_owner",
        headers={"api_key": "key"},
    )

    playlists = response_get.json()

    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_name1"
    assert playlists[0]["description"] == "playlist_description1"


def test_owner_should_be_able_to_edit_its_own_playlist(
    client, custom_requests_mock, drop_tables
):
    response_post = wrap_post_playlist(client)
    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/{response_post.json()['id']}",
        headers={"api_key": "key"},
    )
    assert response_get.status_code == 200

    response_put = client.put(
        f"{API_VERSION_PREFIX}/playlists/{response_post.json()['id']}",
        data={
            "name": "playlist_name_updated",
            "description": "playlist_description_updated",
        },
        headers={"api_key": "key", "uid": "user_playlist_owner"},
    )
    assert response_put.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/{response_post.json()['id']}",
        headers={"api_key": "key"},
    )

    playlist = response_get.json()
    assert response_get.status_code == 200
    assert playlist["id"] == 1
    assert playlist["name"] == "playlist_name_updated"
    assert playlist["description"] == "playlist_description_updated"


def test_colab_should_be_able_to_edit_playlist(
    client, custom_requests_mock, drop_tables
):

    response_post = wrap_post_playlist(client)

    response_put = client.put(
        f"{API_VERSION_PREFIX}/playlists/{response_post.json()['id']}",
        data={
            "name": "playlist_name_updated",
            "description": "playlist_description_updated",
        },
        headers={
            "api_key": "key",
            "uid": "user_playlist_colab",
        },
    )
    assert response_put.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/{response_post.json()['id']}",
        headers={"api_key": "key"},
    )

    playlist = response_get.json()

    assert response_get.status_code == 200
    assert playlist["id"] == 1
    assert playlist["name"] == "playlist_name_updated"
    assert playlist["description"] == "playlist_description_updated"


def test_owner_should_be_able_to_delete_its_own_playlist(
    client, custom_requests_mock, drop_tables
):
    response_post = wrap_post_playlist(client)

    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/playlists/{response_post.json()['id']}",
        headers={"api_key": "key", "uid": "user_playlist_owner"},
    )

    assert response_delete.status_code == 200


def test_user_should_not_be_able_to_delete_other_users_playlist(
    client, custom_requests_mock, drop_tables
):
    response_post = wrap_post_playlist(client)

    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/playlists/{response_post.json()['id']}",
        headers={"api_key": "key", "uid": "user_playlist_colab"},
    )

    assert response_delete.status_code == 403


def test_owner_should_be_able_to_add_songs_to_its_own_playlist(
    client, custom_requests_mock, drop_tables
):
    res_post_playlist = wrap_post_playlist(client)
    res_post_song = post_song(
        client, uid="user_playlist_owner", name="new_song_for_playlist"
    )

    client.post(
        f"{API_VERSION_PREFIX}/playlists/{res_post_playlist.json()['id']}/songs/",
        headers={"api_key": "key", "uid": "user_playlist_owner"},
        data={
            "song_id": res_post_song.json()["id"],
        },
    )

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/{res_post_playlist.json()['id']}",
        headers={"api_key": "key"},
    )

    playlist = response_get.json()

    assert response_get.status_code == 200
    assert playlist["id"] == 1
    assert playlist["name"] == "playlist_name"
    assert playlist["description"] == "playlist_description"
    assert playlist["songs"][0]["name"] == "song_for_playlist1"
    assert playlist["songs"][1]["name"] == "song_for_playlist2"
    assert playlist["songs"][2]["name"] == "new_song_for_playlist"


def test_user_should_not_be_able_to_add_songs_to_other_users_playlist_if_not_collaborator(
    client, custom_requests_mock, drop_tables
):

    res_post_playlist = wrap_post_playlist(client)
    post_user(client, uid="other_user", user_name="other_user_name")
    res_post_song = post_song(client, uid="other_user", name="new_song_for_playlist")

    res_post = client.post(
        f"{API_VERSION_PREFIX}/playlists/{res_post_playlist.json()['id']}/songs/",
        headers={"api_key": "key", "uid": "other_user"},
        data={
            "song_id": res_post_song.json()["id"],
        },
    )

    assert res_post.status_code == 403


def test_user_can_not_add_songs_to_playlist_if_song_does_not_exist(
    client, custom_requests_mock, drop_tables
):
    res_post_playlist = wrap_post_playlist(client)

    res_post = client.post(
        f"{API_VERSION_PREFIX}/playlists/{res_post_playlist.json()['id']}/songs/",
        headers={"api_key": "key", "uid": "user_playlist_owner"},
        data={
            "song_id": 20,
        },
    )

    assert res_post.status_code == 404


def test_owner_can_delete_song_from_playlist(client, custom_requests_mock, drop_tables):
    res_post_playlist = wrap_post_playlist(client)
    res_post_song = post_song(
        client, uid="user_playlist_owner", name="new_song_for_playlist"
    )

    # add song to playlist
    response_post = client.post(
        f"{API_VERSION_PREFIX}/playlists/{res_post_playlist.json()['id']}/songs/",
        headers={"api_key": "key", "uid": "user_playlist_owner"},
        data={
            "song_id": res_post_song.json()["id"],
        },
    )
    assert response_post.status_code == 200

    # delete song from playlist
    res_delete = client.delete(
        f"{API_VERSION_PREFIX}/playlists/{res_post_playlist.json()['id']}/songs/{res_post_song.json()['id']}/",
        headers={"api_key": "key", "uid": "user_playlist_owner"},
    )

    assert res_delete.status_code == 200


def test_get_my_playlists_returns_playlists_in_which_i_am_colab(
    client, custom_requests_mock, drop_tables
):
    wrap_post_playlist(client)

    response_get = client.get(
        f"{API_VERSION_PREFIX}/my_playlists/",
        headers={"api_key": "key", "uid": "user_playlist_colab"},
    )
    assert response_get.status_code == 200
    assert len(response_get.json()) == 1
    assert response_get.json()[0]["name"] == "playlist_name"


def test_get_playlists_by_colab(client, custom_requests_mock, drop_tables):
    wrap_post_playlist(client)

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/?colab=user_playlist_colab",
        headers={"api_key": "key", "uid": "user_playlist_colab"},
    )
    playlists = response_get.json()

    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_name"


def test_add_playlists_colab(client, custom_requests_mock, drop_tables):
    res_post_playlist = wrap_post_playlist(client)
    post_user(client, uid="user_playlist_new_colab", user_name="Paquito")

    client.post(
        f"{API_VERSION_PREFIX}/playlists/{res_post_playlist.json()['id']}/colabs/",
        headers={"api_key": "key", "uid": "user_playlist_owner"},
        data={
            "colab_id": "user_playlist_new_colab",
        },
    )

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/?colab=user_playlist_colab",
        headers={"api_key": "key", "uid": "user_playlist_new_colab"},
    )
    playlists = response_get.json()

    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_name"


def test_colab_cant_add_colab(client, custom_requests_mock, drop_tables):
    res_post_playlist = wrap_post_playlist(client)
    post_user(client, uid="user_playlist_new_colab", user_name="Paquito")

    response_post = client.post(
        f"{API_VERSION_PREFIX}/playlists/{res_post_playlist.json()['id']}/colabs/",
        headers={"api_key": "key", "uid": "user_playlist_colab"},
        data={
            "colab_id": "user_playlist_new_colab",
        },
    )

    assert response_post.status_code == 403


def test_cant_add_colab_to_nonesxistent_playlist(
    client, custom_requests_mock, drop_tables
):
    wrap_post_playlist(client)
    post_user(client, uid="user_playlist_new_colab", user_name="Paquito")

    response_post = client.post(
        f"{API_VERSION_PREFIX}/playlists/999/colabs/",
        headers={"api_key": "key", "uid": "user_playlist_owner"},
        data={
            "colab_id": "user_playlist_new_colab",
        },
    )

    assert response_post.status_code == 404


def test_cant_add_nonesxistent_colab_to_playlist(
    client, custom_requests_mock, drop_tables
):
    res_post_playlist = wrap_post_playlist(client)

    response_post = client.post(
        f"{API_VERSION_PREFIX}/playlists/{res_post_playlist.json()['id']}/colabs/",
        headers={"api_key": "key", "uid": "user_playlist_owner"},
        data={
            "colab_id": "nonexistent_colab",
        },
    )

    assert response_post.status_code == 404


def test_get_playlist_by_id_return_expected_songs(
    client, custom_requests_mock, drop_tables
):
    post_user(client, uid="user_playlist_owner", user_name="Paquito")
    song_id = utils.post_song(
        client, uid="user_playlist_owner", name="new_song_for_playlist"
    ).json()["id"]

    utils.post_playlist(
        client,
        playlist_name="playlist_name",
        uid="user_playlist_owner",
        songs_ids=[song_id],
    )
    response_post_2 = utils.post_playlist(
        client, playlist_name="playlist_name_2", uid="user_playlist_owner"
    )
    utils.post_playlist(
        client, playlist_name="playlist_name_3", uid="user_playlist_owner"
    )

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/{response_post_2.json()['id']}/",
        headers={"api_key": "key", "uid": "user_playlist_owner"},
    )

    playlist = response_get.json()
    assert response_get.status_code == 200
    assert len(playlist["songs"]) == 0


def test_admin_can_add_song_to_playlist_of_another_user(
    client, custom_requests_mock, drop_tables
):
    post_user(client, uid="user_playlist_owner", user_name="Paquito")
    post_user(client, uid="admin_id", user_name="Admin")

    song_id = utils.post_song(
        client, uid="user_playlist_owner", name="new_song_for_playlist"
    ).json()["id"]

    playlist_id = utils.post_playlist(
        client,
        playlist_name="playlist_name",
        uid="user_playlist_owner",
    ).json()["id"]

    response_post = client.post(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}/songs/",
        headers={"api_key": "key", "uid": "admin_id", "role": "admin"},
        data={"song_id": song_id},
    )
    assert response_post.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}/",
        headers={"api_key": "key", "uid": "user_playlist_owner"},
    )

    playlist = response_get.json()
    assert response_get.status_code == 200
    assert len(playlist["songs"]) == 1


def test_admin_can_remove_song_from_playlist_of_another_user(
    client, custom_requests_mock, drop_tables
):
    post_user(client, uid="user_playlist_owner", user_name="Paquito")
    post_user(client, uid="admin_id", user_name="Admin")

    song_id = utils.post_song(
        client, uid="user_playlist_owner", name="new_song_for_playlist"
    ).json()["id"]

    playlist_id = utils.post_playlist(
        client,
        playlist_name="playlist_name",
        uid="user_playlist_owner",
        songs_ids=[song_id],
    ).json()["id"]

    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}/songs/{song_id}/",
        headers={"api_key": "key", "uid": "admin_id", "role": "admin"},
    )
    assert response_delete.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}/",
        headers={"api_key": "key", "uid": "user_playlist_owner"},
    )

    playlist = response_get.json()
    assert response_get.status_code == 200
    assert len(playlist["songs"]) == 0


def test_admin_can_delete_playlist_of_another_user(
    client, custom_requests_mock, drop_tables
):
    post_user(client, uid="user_playlist_owner", user_name="Paquito")
    post_user(client, uid="admin_id", user_name="Admin")

    playlist_id = utils.post_playlist(
        client,
        playlist_name="playlist_name",
        uid="user_playlist_owner",
    ).json()["id"]
    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"api_key": "key", "uid": "admin_id", "role": "admin"},
    )
    assert response_delete.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}/",
        headers={"api_key": "key", "uid": "user_playlist_owner"},
    )

    assert response_get.status_code == 404


def test_admin_can_edit_playlist_of_another_user(
    client, custom_requests_mock, drop_tables
):

    post_user(client, uid="user_playlist_owner", user_name="Paquito")
    post_user(client, uid="admin_id", user_name="Admin")

    playlist_id = utils.post_playlist(
        client,
        playlist_name="playlist_name",
        uid="user_playlist_owner",
    ).json()["id"]
    response_put = client.put(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        headers={"api_key": "key", "uid": "admin_id", "role": "admin"},
        data={"name": "new_playlist_name"},
    )
    assert response_put.status_code == 200

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}/",
        headers={"api_key": "key", "uid": "user_playlist_owner"},
    )

    playlist = response_get.json()
    assert response_get.status_code == 200
    assert playlist["name"] == "new_playlist_name"
