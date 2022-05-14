from typing import Optional, List
import json

API_VERSION_PREFIX = "/api/v3"


def header(uid):
    return {"api_key": "key", "uid": uid}


def post_user(
    client, uid, user_name, wallet="wallet", location="location", interests="interests"
):
    response_post = client.post(
        API_VERSION_PREFIX + "/users/",
        headers={"api_key": "key", "uid": uid},
        data={
            "name": user_name,
            "wallet": wallet,
            "location": location,
            "interests": interests,
        },
    )
    return response_post


def post_song(
    client,
    uid: Optional[str] = "song_creator_id",
    name: Optional[str] = "song_name",
    description: Optional[str] = "song_desc",
    artists: Optional[List[str]] = None,
    genre: Optional[str] = "song_genre",
    file: Optional[str] = "./tests/test.song",
    headers: Optional[dict] = None,
):
    if headers is None:
        headers = header(uid)
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
            },
            files={"file": ("song.txt", f, "plain/text")},
            headers=headers,
        )
    return response_post


def post_album(
    client,
    uid: Optional[str] = "album_creator_id",
    name: Optional[str] = "album_name",
    description: Optional[str] = "album_desc",
    genre: Optional[str] = "album_genre",
    songs_ids: Optional[List[str]] = None,
    sub_level: Optional[int] = 1,
    cover: Optional[str] = "./tests/test.cover",
    headers: Optional[dict] = None,
):
    if headers is None:
        headers = {"api_key": "key", "uid": uid}
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
                "sub_level": sub_level,
                "songs_ids": json.dumps(songs_ids),
                "genre": genre,
            },
            files={"cover": ("cover.txt", f, "plain/text")},
            headers=headers,
        )

    return response_post


def post_playlist(
    client,
    uid: Optional[str] = "playlist_creator_id",
    playlist_name: Optional[str] = "playlist_name",
    description: Optional[str] = "playlist_desc",
    songs_ids: Optional[List[str]] = None,
    colabs_ids: Optional[List[str]] = None,
    headers: Optional[dict] = None,
):

    if headers is None:
        headers = {"api_key": "key"}
    if songs_ids is None:
        songs_ids = []
    if colabs_ids is None:
        colabs_ids = []

    response_post = client.post(
        f"{API_VERSION_PREFIX}/playlists/",
        data={
            "uid": uid,
            "name": playlist_name,
            "description": description,
            "songs_ids": json.dumps(songs_ids),
            "colabs_ids": json.dumps(colabs_ids),
        },
        headers=headers,
    )

    return response_post
