import requests
from typing import Optional, List, Type, Union
import json
from fastapi.testclient import TestClient

from src.main import API_VERSION_PREFIX


def header(uid, role=None):
    headers = {"uid": uid, "api_key": "key"}
    if role is not None:
        headers["role"] = role
    return headers


def post_user(
    client,
    uid,
    user_name="generic_user_name",
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
    uid: Optional[str] = None,
    name: Optional[str] = "song_name",
    description: Optional[str] = "song_desc",
    artists: Optional[List[str]] = None,
    genre: Optional[str] = "song_genre",
    sub_level: Optional[int] = 0,
    file: Optional[str] = "./tests/test.song",
    blocked: Optional[bool] = False,
    headers: Optional[dict] = None,
    role: Optional[str] = "artist",
    album_id: Optional[int] = None,
    unwrap_id: bool = True,
):
    if uid is None:
        uid = get_uid_or_create(client)

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
                "album_id": album_id,
            },
            files={"file": ("song.txt", f, "plain/text")},
            headers=headers,
        )

    if blocked:
        client.put(
            f"{API_VERSION_PREFIX}/songs/{response_post.json()['id']}",
            data={"blocked": True},
            headers={"api_key": "key", "uid": uid, "role": "admin"},
        )

    if unwrap_id:
        return response_post.json()["id"]
    return response_post


def post_album(
    client,
    uid: Optional[str] = None,
    name: Optional[str] = "album_name",
    description: Optional[str] = "album_desc",
    genre: Optional[str] = "album_genre",
    songs_ids: Optional[List[str]] = None,
    cover: Optional[str] = "./tests/test.cover",
    blocked: bool = False,
    headers: Optional[dict] = None,
    role: Optional[str] = "artist",
    unwrap_id: bool = True,
):
    if uid is None:
        uid = get_uid_or_create(client)

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
    if unwrap_id:
        return response_post.json()["id"]
    return response_post


def post_album_with_song(
    client,
    uid: Optional[str] = None,
    album_name="album_name",
    album_genre="album_genre",
    song_name="song_name",
    song_genre="song_genre",
    song_sub_level=0,
):
    song_id = post_song(
        client, uid=uid, name=song_name, genre=song_genre, sub_level=song_sub_level
    )
    return post_album(
        client,
        uid=uid,
        name=album_name,
        genre=album_genre,
        songs_ids=[song_id],
    )


def post_playlist(
    client,
    uid: Optional[str] = None,
    playlist_name: Optional[str] = "playlist_name",
    description: Optional[str] = "playlist_desc",
    songs_ids: Optional[List[str]] = None,
    colabs_ids: Optional[List[str]] = None,
    blocked: Optional[bool] = False,
    headers: Optional[dict] = None,
    unwrap_id: bool = True,
):
    if uid is None:
        uid = get_uid_or_create(client)
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

    if unwrap_id:
        return response_post.json()["id"]
    return response_post


def wrap_post_playlist(client, unwrap_id: bool = True):
    post_user(client, "user_playlist_owner", user_name="Ricardito")
    post_user(client, "user_playlist_colab", user_name="Fernandito")
    playlist_id_1 = post_song(
        client, uid="user_playlist_owner", name="song_for_playlist1"
    )
    playlist_id_2 = post_song(
        client, uid="user_playlist_owner", name="song_for_playlist2"
    )
    colabs_id = ["user_playlist_colab"]
    songs_id = [playlist_id_1, playlist_id_2]
    return post_playlist(
        client,
        uid="user_playlist_owner",
        playlist_name="playlist_name",
        description="playlist_description",
        colabs_ids=colabs_id,
        songs_ids=songs_id,
        unwrap_id=unwrap_id,
    )


def block_song(client, song_id: int):
    post_user(client, "__blocker__id__", user_name="__blocker__name__")
    response_put = client.put(
        f"{API_VERSION_PREFIX}/songs/{song_id}",
        data={"blocked": True},
        headers={"api_key": "key", "uid": "__blocker__id__", "role": "admin"},
    )
    assert response_put.status_code == 200
    return response_put


def post_review(
    client,
    album_id: int,
    uid: Optional[str] = None,
    text: Optional[str] = "review text",
    score: Optional[int] = 5,
    role: Optional[str] = "listener",
):
    return post_json(
        client,
        f"/albums/{album_id}/reviews/",
        json={"text": text, "score": score},
        uid=uid,
        role=role,
    )


def add_song_to_favorites(client, uid, song_id):
    return post(client, f"/users/{uid}/favorites/songs/?song_id={song_id}", uid=uid, data={})


def get_favorite_songs(client, uid, role="listener"):
    return get(client, f"/users/{uid}/favorites/songs/", uid=uid, role=role)


def delete_song_from_favorites(client, uid, song_id):
    response_delete = client.delete(
        f"{API_VERSION_PREFIX}/users/{uid}/favorites/songs/?song_id={song_id}",
        headers={"api_key": "key", "uid": uid},
    )
    return response_delete


def get_favorite_albums(client, uid, role: Optional[str] = "listener"):
    return get(client, f"/users/{uid}/favorites/albums/", uid=uid, role=role)


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
    post_user(client, "__blocker__id__", user_name="__blocker__name__")
    return put(client, f"/albums/{id}", data={"blocked": True}, uid="__blocker__id__", role="admin")


def remove_album_from_favorites(client, uid, album_id):
    return delete(client, f"/users/{uid}/favorites/albums/?album_id={album_id}", uid=uid)


def get_favorite_playlists(client, uid, role="listener"):
    return get(client, f"/users/{uid}/favorites/playlists/", uid=uid, role=role)


def add_playlist_to_favorites(client, uid, playlist_id, role="listener"):
    return post(client, f"/users/{uid}/favorites/playlists/?playlist_id={playlist_id}", uid=uid, role=role, data={})


def block_playlist(client, playlist_id: int):
    post_user(client, "__blocker__id__", user_name="__blocker__name__")
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
    response = post_user(client, user_id, user_name)
    assert response.status_code == 200

    response = client.post(
        f"{API_VERSION_PREFIX}/subscriptions/",
        headers={"api_key": "key", "uid": user_id},
        json={"sub_level": sub_level},
    )
    assert response.status_code == 200

    response = client.post(
        f"{API_VERSION_PREFIX}/subscriptions/",
        headers={"api_key": "key", "uid": user_id},
        json={"sub_level": sub_level},
    )
    return response


def delete_user(client, user_id: str):
    return delete(client, f"/users/{user_id}", uid=user_id)


def get(
    client,
    endpoint: str,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
    offset: Optional[Union[int, str]] = None,
    limit: Optional[Union[int, str]] = None,
):
    if uid is None:
        uid = get_uid_or_create(client)
    headers = {
        "api_key": "key",
        "uid": uid,
        "role": role,
    }
    params = {}
    if limit is not None:
        params["offset"] = offset
        params["limit"] = limit

    response = client.get(
        f"{API_VERSION_PREFIX}{endpoint}",
        headers=headers,
        params=params,
    )
    if limit is None:
        if response.status_code < 299 and "items" in response.json():
            items = response.json()["items"]
            resp = requests.models.Response()
            resp.status_code = response.status_code
            resp._content = json.dumps(items, indent=2).encode("utf-8")
            response = resp
    if unwrap:
        return response.json()
    return response


def post(
    client,
    endpoint: str,
    data: dict,
    uid: Optional[str] = None,
    role: str = "listener",
    files: Optional[dict] = None,
    unwrap: bool = False,
):
    if uid is None:
        uid = get_uid_or_create(client)

    response = client.post(
        f"{API_VERSION_PREFIX}{endpoint}",
        headers={"api_key": "key", "uid": uid, "role": role},
        data=data,
        files=files,
    )
    if unwrap:
        return response.json()
    return response


def post_json(
    client,
    endpoint: str,
    json: dict,
    uid: Optional[str] = None,
    role: str = "listener",
    files: Optional[dict] = None,
    unwrap: bool = False,
):
    if uid is None:
        uid = get_uid_or_create(client)

    response = client.post(
        f"{API_VERSION_PREFIX}{endpoint}",
        headers={"api_key": "key", "uid": uid, "role": role},
        json=json,
        files=files,
    )
    if unwrap:
        return response.json()
    return response


def delete(
    client,
    endpoint: str,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    if uid is None:
        uid = get_uid_or_create(client)

    response = client.delete(
        f"{API_VERSION_PREFIX}{endpoint}",
        headers={"api_key": "key", "uid": uid, "role": role},
    )
    if unwrap:
        return response.json()
    return response


def put(
    client,
    endpoint: str,
    data: dict,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    if uid is None:
        uid = get_uid_or_create(client)

    response = client.put(
        f"{API_VERSION_PREFIX}{endpoint}",
        data=data,
        headers={"api_key": "key", "uid": uid, "role": role},
    )
    if unwrap:
        return response.json()
    return response


def put_json(
    client,
    endpoint: str,
    json: dict,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    if uid is None:
        uid = get_uid_or_create(client)

    response = client.put(
        f"{API_VERSION_PREFIX}{endpoint}",
        json=json,
        headers={"api_key": "key", "uid": uid, "role": role},
    )
    if unwrap:
        return response.json()
    return response


def get_album(
    client,
    album_id: int,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return get(client, f"/albums/{album_id}", uid, role, unwrap)


def add_query(endpoint: str, query: str):
    if "?" in endpoint:
        return f"{endpoint}&{query}"
    return f"{endpoint}?{query}"


def search_albums(
    client,
    artist: Optional[str] = None,
    genre: Optional[str] = None,
    name: Optional[str] = None,
    creator: Optional[str] = None,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
):
    endpoint = "/albums/"
    for search_term, value in (
        ("artist", artist),
        ("genre", genre),
        ("name", name),
        ("creator", creator),
    ):
        if value is not None:
            endpoint = add_query(endpoint, f"{search_term}={value}")

    return get(client, endpoint, uid=uid, role=role, unwrap=unwrap, offset=offset, limit=limit)


def get_my_albums(client, uid: str, role: str = "listener", unwrap=False):
    return get(client, f"/my_albums/", uid, role, unwrap)


def put_album(
    client,
    album_id: int,
    data: dict,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return put(client, f"/albums/{album_id}", data, uid, role, unwrap)


def delete_album(
    client,
    album_id: int,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return delete(client, f"/albums/{album_id}", uid, role, unwrap)


def get_song(
    client,
    song_id: int,
    uid: Optional[str] = None,
    role: Optional[str] = "listener",
    unwrap=False,
):
    return get(client, f"/songs/{song_id}", uid, role, unwrap)


def get_my_songs(
    client,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
):
    return get(client, f"/my_songs/", uid, role, unwrap, offset=offset, limit=limit)


def search_songs(
    client,
    artist: Optional[str] = None,
    genre: Optional[str] = None,
    name: Optional[str] = None,
    creator: Optional[str] = None,
    sub_level: Optional[int] = None,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
):
    endpoint = "/songs/"
    for search_term, value in (
        ("artist", artist),
        ("genre", genre),
        ("name", name),
        ("creator", creator),
        ("sub_level", sub_level),
    ):
        if value is not None:
            endpoint = add_query(endpoint, f"{search_term}={value}")

    return get(client, endpoint, uid=uid, role=role, unwrap=unwrap, offset=offset, limit=limit)


def put_song(
    client,
    song_id: int,
    data: dict,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return put(client, f"/songs/{song_id}", data, uid, role, unwrap)


def delete_song(
    client,
    song_id: int,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return delete(client, f"/songs/{song_id}", uid, role, unwrap)


def get_songs_by_creator(
    client,
    creator_id: str,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return get(client, f"/songs/?creator={creator_id}", uid, role, unwrap)


def get_playlist(
    client,
    playlist_id: int,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return get(client, f"/playlists/{playlist_id}", uid, role, unwrap)


def get_my_playlists(
    client,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return get(client, f"/my_playlists/", uid, role, unwrap)


def search_playlists(
    client,
    uid: Optional[str] = None,
    colab: Optional[str] = None,
    creator: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
):
    endpoint = "/playlists/"
    for search_term, value in (
        ("colab", colab),
        ("creator", creator),
    ):
        if value is not None:
            endpoint = add_query(endpoint, f"{search_term}={value}")
    return get(client, endpoint, uid=uid, role=role, unwrap=unwrap, offset=offset, limit=limit)


def put_playlist(
    client,
    playlist_id: int,
    data: dict,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return put(client, f"/playlists/{playlist_id}", data, uid, role, unwrap)


def delete_playlist(
    client,
    playlist_id: int,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return delete(client, f"/playlists/{playlist_id}", uid, role, unwrap)


def add_playlist_song(
    client,
    playlist_id: int,
    song_id: int,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return post(
        client,
        f"/playlists/{playlist_id}/songs/",
        {"song_id": song_id},
        uid,
        role,
        unwrap=unwrap,
    )


def remove_playlist_song(
    client,
    playlist_id: int,
    song_id: int,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return delete(
        client,
        f"/playlists/{playlist_id}/songs/{song_id}/",
        uid,
        role,
        unwrap,
    )


def add_playlist_colab(
    client,
    playlist_id: int,
    colab_id: str,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return post(
        client,
        f"/playlists/{playlist_id}/colabs/",
        {"colab_id": colab_id},
        uid,
        role,
        unwrap=unwrap,
    )


def post_users(client: Type[TestClient], *users_ids):
    for user_id in users_ids:
        post_user(client, user_id)


def get_uid_or_create(client):
    users = client.get(f"{API_VERSION_PREFIX}/users", headers={"api_key": "key"}).json()["items"]
    if len(users) == 0:
        uid = "__user_id__"
        post_user(client, uid)
    else:
        uid = users[0]["id"]
    return uid


def get_album_comments(
    client,
    album_id: int,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
):
    return get(client, f"/albums/{album_id}/comments/", uid, role, unwrap, offset, limit)


def post_comment(
    client,
    album_id: int,
    message: str = "comment_text",
    parent_id: Optional[int] = None,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap_id=True,
):
    response = post_json(
        client,
        f"/albums/{album_id}/comments/",
        {"text": message, "parent_id": parent_id},
        uid,
        role,
        unwrap=unwrap_id,
    )
    if unwrap_id:
        return response["id"]
    return response


def get_user_comments(
    client,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return get(client, f"/users/comments/", uid, role, unwrap)


def put_comment(
    client,
    comment_id: int,
    message: str,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return put_json(
        client,
        f"/albums/comments/{comment_id}/",
        {"text": message},
        uid,
        role,
        unwrap,
    )


def delete_comment(
    client,
    comment_id: int,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return delete(client, f"/albums/comments/{comment_id}/", uid, role, unwrap)


def get_reviews_of_album(
    client,
    album_id: int,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
    offset: Optional[str] = None,
    limit: Optional[int] = None,
):
    return get(client, f"/albums/{album_id}/reviews/", uid, role, unwrap, offset, limit)


def delete_review_of_album(
    client,
    album_id: int,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return delete(client, f"/albums/{album_id}/reviews/", uid, role, unwrap)


def put_review_of_album(
    client,
    album_id: int,
    text: Optional[str],
    score: Optional[int],
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return put_json(
        client,
        f"/albums/{album_id}/reviews/",
        {"text": text, "score": score},
        uid,
        role,
        unwrap,
    )


def get_users(
    client,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
):
    return get(client, f"/users/", uid, role, unwrap, offset, limit)


def get_user_reviews(
    client,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
):
    return get(client, f"/users/{uid}/reviews/", uid, role, unwrap, offset, limit)


def get_user(
    client,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
):
    return get(client, f"/users/{uid}/", uid, role, unwrap)


def get_streamings(
    client,
    uid: Optional[str] = None,
    role: str = "listener",
    unwrap=False,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
):
    return get(client, f"/streamings/", uid, role, unwrap, offset, limit)
