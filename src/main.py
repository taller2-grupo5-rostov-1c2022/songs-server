from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from pydantic import BaseModel
import os

app = FastAPI()

API_KEY = os.environ.get("API_KEY") or "key"
API_KEY_NAME = "api_key"


async def get_api_key(
    api_key_header: str = Security(APIKeyHeader(name=API_KEY_NAME, auto_error=True)),
):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403)


class Song(BaseModel):
    name: str


songs = [Song(name="song1"), Song(name="song2")]


@app.get("/")
def healthcheck():
    """Endpoint Healthcheck"""
    return "ok"


@app.get("/api/v1/songs/")
def get_all_songs(_api_key: APIKey = Depends(get_api_key)):
    """Returns all songs"""
    return songs


@app.get("/api/v1/songs/{song_id}")
def get_song_by_id(song_id: int, _api_key: APIKey = Depends(get_api_key)):
    """Returns a song by its id or 404 if not found"""
    if len(songs) <= song_id:
        raise HTTPException(status_code=404, detail="Song not found")
    return songs[song_id]


@app.post("/api/v1/songs/")
def post_song(song: Song, _api_key: APIKey = Depends(get_api_key)):
    """Creates a song and returns its id"""
    songs.append(song)
    return {"id": len(songs) - 1}
