from typing import Optional, List
import json

from src.main import API_VERSION_PREFIX


def header(uid, role=None):
    headers = {"uid": uid, "api_key": "key"}
    if role is not None:
        headers["role"] = role
    return headers


def post_user(
    client,
    uid,
    user_name,
    location="location",
    interests="interests",
    include_pfp=False,
):
    data = {
        "name": user_name,
        "location": location,
        "interests": interests,
    }
    if include_pfp:
        with open("./pfp.img", "wb") as f:
            f.write(b"test")
        with open("./pfp.img", "rb") as f:
            files = {"img": ("pfp.img", f, "plain/text")}
            response_post = client.post(
                API_VERSION_PREFIX + "/users/",
                headers={"api_key": "key", "uid": uid},
                data=data,
                files=files,
            )
            assert response_post.status_code == 200
    else:
        response_post = client.post(
            API_VERSION_PREFIX + "/users/",
            headers={"api_key": "key", "uid": uid},
            data=data,
        )

    return response_post


def post_song(
    client,
    uid: Optional[str] = "song_creator_id",
    name: Optional[str] = "song_name",
    description: Optional[str] = "song_desc",
    artists: Optional[List[str]] = None,
    genre: Optional[str] = "song_genre",
    sub_level: Optional[int] = 0,
    file: Optional[str] = "./tests/test.song",
    blocked: Optional[bool] = False,
    headers: Optional[dict] = None,
    role: Optional[str] = "artist",
):
    if headers is None:
        headers = header(uid, role=role)
    if artists is None:
        artists = ["song_artist_name"]

    with open(file, "wb") as f:
        f.write(b"test")
    with open(file, "rb") as f:
        response_post = client.post(
            API_VERSION_PREFIX + "/songs/",
            data={
                "name": name,
                "description": description,
                "artists": json.dumps(artists),
                "genre": genre,
                "sub_level": sub_level,
            },
            files={"file": ("song.txt", f, "plain/text")},
            headers=headers,
        )

    if blocked:
        response_put = client.put(
            f"{API_VERSION_PREFIX}/songs/{response_post.json()['id']}",
            data={"blocked": True},
            headers={"api_key": "key", "uid": uid, "role": "admin"},
        )
        assert response_put.status_code == 200
    return response_post


def get_song_by_id(
    client, song_id: int, uid: Optional[str] = None, role: Optional[str] = "listener"
):
    if uid is None:
        uid = post_user(client, "__user_id__", "__user_name__").json()["id"]

    response = client.get(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        headers={"api_key": "key", "uid": uid, "role": role},
    )
    return response


def post_album(
    client,
    uid: Optional[str] = "album_creator_id",
    name: Optional[str] = "album_name",
    description: Optional[str] = "album_desc",
    genre: Optional[str] = "album_genre",
    songs_ids: Optional[List[str]] = None,
    cover: Optional[str] = "./tests/test.cover",
    blocked: bool = False,
    headers: Optional[dict] = None,
    role: Optional[str] = "artist",
):
    if headers is None:
        headers = header(uid, role=role)
    if songs_ids is None:
        songs_ids = []

    with open(cover, "wb") as f:
        f.write(b"test")
    with open(cover, "rb") as f:
        response_post = client.post(
            API_VERSION_PREFIX + "/albums/",
            data={
                "name": name,
                "description": description,
                "songs_ids": json.dumps(songs_ids),
                "genre": genre,
            },
            files={"cover": ("cover.txt", f, "plain/text")},
            headers=headers,
        )

    if blocked:
        response_put = client.put(
            f"{API_VERSION_PREFIX}/albums/{response_post.json()['id']}",
            data={"blocked": True},
            headers={"api_key": "key", "uid": uid, "role": "admin"},
        )
        assert response_put.status_code == 200
    return response_post


def post_album_with_song(
    client,
    uid="user_id",
    album_name="album_name",
    album_genre="album_genre",
    song_name="song_name",
    song_genre="song_genre",
    song_sub_level=0,
):
    song_id = post_song(
        client, uid=uid, name=song_name, genre=song_genre, sub_level=song_sub_level
    ).json()["id"]
    return post_album(
        client,
        uid=uid,
        name=album_name,
        genre=album_genre,
        songs_ids=[song_id],
    )


def post_playlist(
    client,
    uid: Optional[str] = "playlist_creator_id",
    playlist_name: Optional[str] = "playlist_name",
    description: Optional[str] = "playlist_desc",
    songs_ids: Optional[List[str]] = None,
    colabs_ids: Optional[List[str]] = None,
    blocked: Optional[bool] = False,
    headers: Optional[dict] = None,
):

    if headers is None:
        headers = {
            "api_key": "key",
            "uid": uid,
        }
    if songs_ids is None:
        songs_ids = []
    if colabs_ids is None:
        colabs_ids = []

    response_post = client.post(
        f"{API_VERSION_PREFIX}/playlists/",
        data={
            "name": playlist_name,
            "description": description,
            "songs_ids": json.dumps(songs_ids),
            "colabs_ids": json.dumps(colabs_ids),
        },
        headers=headers,
    )

    if blocked:
        response_put = client.put(
            f"{API_VERSION_PREFIX}/playlists/{response_post.json()['id']}",
            data={"blocked": True},
            headers={"api_key": "key", "uid": uid, "role": "admin"},
        )
        assert response_put.status_code == 200
    return response_post


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


def block_song(client, song_id: int):
    post_user(client, uid="__blocker__id__", user_name="__blocker__name__")
    response_put = client.put(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        data={"blocked": True},
        headers={"api_key": "key", "uid": "__blocker__id__", "role": "admin"},
    )
    assert response_put.status_code == 200
    return response_put


def post_review(
    client,
    uid: str,
    album_id: int,
    text: Optional[str] = "review text",
    score: Optional[int] = 5,
):
    response_post = client.post(
        f"{API_VERSION_PREFIX}/albums/{album_id}/reviews/",
        json={"text": text, "score": score},
        headers={"api_key": "key", "uid": uid},
    )
    return response_post


def add_song_to_favorites(client, uid, song_id):
    response_post = client.post(
        f"{API_VERSION_PREFIX}/users/{uid}/favorites/songs/?song_id={song_id}",
        headers={"api_key": "key", "uid": uid},
    )
    return response_post


def get_favorite_songs(client, uid, role="listener"):
    response = client.get(
        f"{API_VERSION_PREFIX}/users/{uid}/favorites/songs/",
        headers={"api_key": "key", "uid": uid, "role": role},
    )
    return response


def delete_song_from_favorites(client, uid, song_id):
    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/users/{uid}/favorites/songs/?song_id={song_id}",
        headers={"api_key": "key", "uid": uid},
    )
    return response_delete


def get_favorite_albums(client, uid, role: Optional[str] = "listener"):
    response = client.get(
        f"{API_VERSION_PREFIX}/users/{uid}/favorites/albums/",
        headers={"api_key": "key", "uid": uid, "role": role},
    )
    return response


def add_album_to_favorites(client, uid, album_id):
    response_post = client.post(
        f"{API_VERSION_PREFIX}/users/{uid}/favorites/albums/?album_id={album_id}",
        headers={"api_key": "key", "uid": uid},
    )
    return response_post


def add_song_to_album(client, uid: str, song_id: int, album_id: int):
    response_get = client.get(
        f"{API_VERSION_PREFIX}/albums/{album_id}/songs/",
        headers={"api_key": "key", "uid": uid},
    )
    songs_ids = [song["id"] for song in response_get.json()]
    songs_ids.append(song_id)
    response_put = client.put(
        f"{API_VERSION_PREFIX}/albums/{album_id}/songs/",
        data={"songs_ids": json.dumps(songs_ids)},
        headers={"api_key": "key", "uid": uid},
    )
    return response_put


def block_album(client, id: int):
    post_user(client, uid="__blocker__id__", user_name="__blocker__name__")
    response_put = client.put(
        f"{API_VERSION_PREFIX}/albums/{id}",
        data={"blocked": True},
        headers={"api_key": "key", "uid": "__blocker__id__", "role": "admin"},
    )
    assert response_put.status_code == 200
    return response_put


def remove_album_from_favorites(client, uid, album_id):
    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/users/{uid}/favorites/albums/?album_id={album_id}",
        headers={"api_key": "key", "uid": uid},
    )
    return response_delete


def get_favorite_playlists(client, uid, role="listener"):
    response = client.get(
        f"{API_VERSION_PREFIX}/users/{uid}/favorites/playlists/",
        headers={"api_key": "key", "uid": uid, "role": role},
    )
    return response


def add_playlist_to_favorites(client, uid, playlist_id, role="listener"):
    response_post = client.post(
        f"{API_VERSION_PREFIX}/users/{uid}/favorites/playlists/?playlist_id={playlist_id}",
        headers={"api_key": "key", "uid": uid, "role": role},
    )
    return response_post


def block_playlist(client, playlist_id: int):
    post_user(client, uid="__blocker__id__", user_name="__blocker__name__")
    response_put = client.put(
        f"{API_VERSION_PREFIX}/playlists/{playlist_id}",
        data={"blocked": True},
        headers={"api_key": "key", "uid": "__blocker__id__", "role": "admin"},
    )
    assert response_put.status_code == 200
    return response_put


def remove_playlist_from_favorites(client, uid, playlist_id):
    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/users/{uid}/favorites/playlists/?playlist_id={playlist_id}",
        headers={"api_key": "key", "uid": uid},
    )
    return response_delete


def post_comment(client, uid: str, album_id: int, text: str, parent_id: int = None):
    response_post = client.post(
        f"{API_VERSION_PREFIX}/albums/{album_id}/comments/",
        json={"text": text, "parent_id": parent_id},
        headers={"api_key": "key", "uid": uid},
    )
    return response_post


def post_streaming(client, uid: str, name="streaming_name", include_img=False):
    data = {"name": name}

    if include_img:
        with open("./streaming.img", "wb") as f:
            f.write(b"test")
        with open("./streaming.img", "rb") as f:
            files = {"img": ("streaming.img", f, "plain/text")}
            response_post = client.post(
                API_VERSION_PREFIX + "/streamings/",
                headers={"api_key": "key", "uid": uid, "role": "artist"},
                data=data,
                files=files,
            )
    else:
        response_post = client.post(
            API_VERSION_PREFIX + "/streamings/",
            headers={"api_key": "key", "uid": uid, "role": "artist"},
            data=data,
        )

    return response_post


def post_user_with_sub_level(client, user_id: str, user_name: str, sub_level: int):
    post_user(client, user_id, user_name)
    response = client.post(
        f"{API_VERSION_PREFIX}/subscriptions/",
        headers={"api_key": "key", "uid": "user_id"},
        json={"sub_level": sub_level},
    )

    assert response.status_code == 200

    response = client.post(
        f"{API_VERSION_PREFIX}/subscriptions/",
        headers={"api_key": "key", "uid": "user_id"},
        json={"sub_level": sub_level},
    )
    return response
