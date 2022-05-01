from typing import Optional, List
import json

API_VERSION_PREFIX = "/api/v3"


def create_user(client, user_id, user_name):
    response_post = client.post(
        API_VERSION_PREFIX + f"/users/?user_id={user_id}&user_name={user_name}",
        headers={"api_key": "key"},
    )
    return response_post


def post_song(
    client,
    user_id: Optional[str] = "song_creator_id",
    name: Optional[str] = "song_name",
    description: Optional[str] = "song_desc",
    artists: Optional[List[str]] = None,
    genre: Optional[str] = "song_genre",
    file: Optional[str] = "./tests/test.song",
    headers: Optional[dict] = None,
):
    if headers is None:
        headers = {"api_key": "key"}
    if artists is None:
        artists = ["song_artist_name"]

    with open(file, "wb") as f:
        f.write(b"test")
    with open(file, "rb") as f:
        response_post = client.post(
            API_VERSION_PREFIX + "/songs/",
            data={
                "user_id": user_id,
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
    user_id: Optional[str] = "album_creator_id",
    name: Optional[str] = "album_name",
    description: Optional[str] = "album_desc",
    artists: Optional[List[str]] = None,
    genre: Optional[str] = "album_genre",
    songs_ids: Optional[List[str]] = None,
    headers: Optional[dict] = None,
):
    if headers is None:
        headers = {"api_key": "key"}
    if artists is None:
        artists = ["artist_name_1", "artist_name_2"]
    if songs_ids is None:
        songs_ids = []

    response_post = client.post(
        API_VERSION_PREFIX + "/albums/",
        data={
            "user_id": user_id,
            "name": name,
            "description": description,
            "artists": json.dumps(artists),
            "genre": genre,
            "songs_ids": json.dumps(songs_ids),
        },
        headers=headers,
    )

    return response_post