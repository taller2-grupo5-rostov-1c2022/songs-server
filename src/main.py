from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
import os
from src.classes import SongUpdate, Song


os.environ["TESTING"] = "1"

if os.environ.get("TESTING") == "1":
    print("RUNNING IN TESTING MODE: MOCKING ACTIVATED")
    from src.mocks.firebase.database import db
    from src.mocks.firebase.bucket import bucket
else:
    from src.firebase.access import db, bucket

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


@app.get("/")
def healthcheck():
    """Endpoint Healthcheck"""
    return "ok"


@app.get("/api/v1/songs/")
def get_all_songs(_api_key: APIKey = Depends(get_api_key)):
    """Returns all songs"""
    songs = db.collection("songs").stream()
    songs_dict = {}
    for song in songs:
        print(songs)
        songs_dict[song.id] = song.to_dict()
    return songs_dict


@app.get("/api/v1/songs/{song_id}")
def get_song_by_id(song_id: str, _api_key: APIKey = Depends(get_api_key)):
    """Returns a song by its id or 404 if not found"""
    db_entry = db.collection("songs").document(song_id).get()
    if not db_entry.exists:
        raise HTTPException(status_code=404, detail="Song not found")

    blob = bucket.blob(db_entry.id)
    song_file_bytes = blob.download_as_bytes()
    db_entry_dict = db_entry.to_dict()
    db_entry_dict["file"] = song_file_bytes
    return db_entry_dict


@app.post("/api/v1/songs/")
def post_song(song: Song, _api_key: APIKey = Depends(get_api_key)):
    """Creates a song and returns its id"""
    ref = db.collection("songs").document()
    ref.set(song.info.dict())

    blob = bucket.blob(ref.id)
    blob.upload_from_string(song.file)
    return {"id": ref.id}


@app.delete("/api/v1/songs/")
def delete_song(song_id: str, _api_key: APIKey = Depends(get_api_key)):
    """Deletes a song given its id or 404 if not found"""
    try:
        db.collection("songs").document(song_id).delete()
        blob = bucket.blob(song_id)
        blob.delete()
    # TODO: catchear solo NotFound
    except Exception as entry_not_found:
        raise HTTPException(status_code=404, detail="Song not found") from entry_not_found
    return song_id


@app.put("/api/v1/songs/")
def update_song(song_id: str, song_update: SongUpdate, _api_key: APIKey = Depends(get_api_key)):
    """Updates song and returns its id or 404 if not found"""
    if song_update.info is not None:
        try:
            db.collection("songs").document(song_id).update(song_update.info.dict(exclude_unset=True))
        except Exception as entry_not_found:
            raise HTTPException(status_code=404, detail="Song not found") from entry_not_found
    if song_update.file is not None:
        try:
            blob = bucket.blob(song_id)
            blob.upload_from_string(song_update.file)
        except Exception as entry_not_found:
            raise HTTPException(status_code=404, detail="Song not found") from entry_not_found

    return song_id
