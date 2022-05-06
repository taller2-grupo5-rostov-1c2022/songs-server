from tests.utils import API_VERSION_PREFIX, post_song, post_user, post_playlist


def wrap_post_playlist(client):
    post_user(client, uid="user_playlist_owner", user_name="Ricardito")
    post_user(client, uid="user_playlist_colab", user_name="Fernandito")
    res_1 = post_song(client, uid="user_playlist_owner", name="song_for_playlist1")
    res_2 = post_song(client, uid="user_playlist_owner", name="song_for_playlist2")
    colabs_id = ["user_playlist_colab"]
    songs_id = [res_1.json()["id"], res_2.json()["id"]]
    response_post = post_playlist(
        client,
        uid="user_playlist_owner",
        playlist_name="playlist_name",
        description="playlist_description",
        colabs_ids=colabs_id,
        songs_ids=songs_id,
    )
    return response_post


def test_get_playlist_by_id_should_return_404_if_playlist_not_found(client):
    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/1", headers={"api_key": "key"}
    )

    assert response.status_code == 404


def test_get_playlist_by_id_should_return_401_if_not_authorized(client):
    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/1", headers={"api_key": "wrong_key"}
    )

    assert response.status_code == 403


def test_get_playlist_should_return_empty_response(client):
    response = client.get(
        f"{API_VERSION_PREFIX}/playlists/", headers={"api_key": "key"}
    )
    assert response.status_code == 200
    assert response.json() == []


def test_post_playlist_should_return_its_id(client):
    response = wrap_post_playlist(client)

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_playlist_by_id(client):
    response_post = wrap_post_playlist(client)

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/{response_post.json()['id']}",
        headers={"api_key": "key"},
    )

    playlist = response_get.json()

    assert response_get.status_code == 200
    assert playlist["id"] == 1
    assert playlist["name"] == "playlist_name"
    assert playlist["description"] == "playlist_description"
    assert playlist["songs"][0]["name"] == "song_for_playlist1"
    assert playlist["songs"][1]["name"] == "song_for_playlist2"


def test_get_all_playlists_with_no_specific_uid(client):

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


def test_get_playlist_from_uid(client):

    # Two users
    post_user(client, uid="user_playlist_owner", user_name="Ricardito")
    post_user(client, uid="user_playlist_colab", user_name="Fernandito")

    # Two songs
    res_1 = post_song(client, uid="user_playlist_owner", name="song_for_playlist1")
    res_2 = post_song(client, uid="user_playlist_owner", name="song_for_playlist2")
    colabs_id_playlist_1 = ["user_playlist_colab"]
    colabs_id_playlist_2 = ["user_playlist_owner"]
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
        f"{API_VERSION_PREFIX}/playlists/?creator=user_playlist_owner",
        headers={"api_key": "key"},
    )

    playlists = response_get.json()

    assert response_get.status_code == 200
    assert len(playlists) == 1
    assert playlists[0]["name"] == "playlist_name1"
    assert playlists[0]["description"] == "playlist_description1"


def test_owner_should_be_able_to_edit_its_own_playlist(client):
    response_post = wrap_post_playlist(client)

    response_put = client.put(
        f"{API_VERSION_PREFIX}/playlists/{response_post.json()['id']}",
        data={
            "name": "playlist_name_updated",
            "description": "playlist_description_updated",
            "uid": "user_playlist_owner",
        },
        headers={"api_key": "key"},
    )

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/{response_put.json()['id']}",
        headers={"api_key": "key"},
    )

    playlist = response_get.json()

    assert response_get.status_code == 200
    assert playlist["id"] == 1
    assert playlist["name"] == "playlist_name_updated"
    assert playlist["description"] == "playlist_description_updated"


def test_colab_should_be_able_to_edit_playlist(client):

    response_post = wrap_post_playlist(client)

    response_put = client.put(
        f"{API_VERSION_PREFIX}/playlists/{response_post.json()['id']}",
        data={
            "uid": "user_playlist_colab",
            "name": "playlist_name_updated",
            "description": "playlist_description_updated",
        },
        headers={"api_key": "key"},
    )

    response_get = client.get(
        f"{API_VERSION_PREFIX}/playlists/{response_put.json()['id']}",
        headers={"api_key": "key"},
    )

    playlist = response_get.json()
    print(playlist)

    assert response_get.status_code == 200
    assert playlist["id"] == 1
    assert playlist["name"] == "playlist_name_updated"
    assert playlist["description"] == "playlist_description_updated"


def test_owner_should_be_able_to_delete_its_own_playlist(client):
    response_post = wrap_post_playlist(client)

    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/playlists/{response_post.json()['id']}?uid=user_playlist_owner",
        headers={"api_key": "key"},
    )

    assert response_delete.status_code == 200


def test_user_should_not_be_able_to_delete_other_users_playlist(client):
    response_post = wrap_post_playlist(client)

    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/playlists/{response_post.json()['id']}?uid=user_playlist_colab",
        headers={"api_key": "key"},
    )

    assert response_delete.status_code == 403