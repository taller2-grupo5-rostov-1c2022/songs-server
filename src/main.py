from fastapi import FastAPI, HTTPException, Depends, Security, UploadFile
from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi.middleware.cors import CORSMiddleware
from src.classes import SongUpdate, Song

from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres.models import SongModel

import os

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


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        songs_dict[song.id] = song.to_dict()
    return songs_dict


@app.get("/api/v1/songs/{song_id}")
def get_song_by_id(song_id: str, _api_key: APIKey = Depends(get_api_key)):
    """Returns a song by its id or 404 if not found"""
    db_entry = db.collection("songs").document(song_id).get()
    if not db_entry.exists:
        raise HTTPException(status_code=404, detail="Song not found")

    blob = bucket.blob("songs/" + db_entry.id)
    song_file_bytes = blob.download_as_bytes()
    db_entry_dict = db_entry.to_dict()
    db_entry_dict["file"] = song_file_bytes
    return db_entry_dict


@app.post("/api/v1/songs/")
def post_song(song: Song, _api_key: APIKey = Depends(get_api_key)):
    """Creates a song and returns its id"""
    ref = db.collection("songs").document()
    ref.set(song.info.dict())

    blob = bucket.blob("songs/" + ref.id)
    blob.upload_from_string(song.file)
    return {"id": ref.id}


@app.delete("/api/v1/songs/")
def delete_song(song_id: str, _api_key: APIKey = Depends(get_api_key)):
    """Deletes a song given its id or 404 if not found"""
    try:
        db.collection("songs").document(song_id).delete()
        blob = bucket.blob("songs/" + song_id)
        blob.delete()
    # TODO: catchear solo NotFound
    except Exception as entry_not_found:
        raise HTTPException(
            status_code=404, detail="Song not found"
        ) from entry_not_found
    return song_id


@app.put("/api/v1/songs/")
def update_song(
    song_id: str, song_update: SongUpdate, _api_key: APIKey = Depends(get_api_key)
):
    """Updates song and returns its id or 404 if not found"""
    if song_update.info is not None:
        try:
            db.collection("songs").document(song_id).update(
                song_update.info.dict(exclude_unset=True)
            )
        except Exception as entry_not_found:
            raise HTTPException(
                status_code=404, detail="Song not found"
            ) from entry_not_found
    if song_update.file is not None:
        try:
            blob = bucket.blob("songs/" + song_id)
            blob.upload_from_string(song_update.file)
        except Exception as entry_not_found:
            raise HTTPException(
                status_code=404, detail="Song not found"
            ) from entry_not_found

    return song_id


################################################################################


@app.get("/api/v2/songs/")
def get_all_songs2(
    pdb: Session = Depends(get_db), _api_key: APIKey = Depends(get_api_key)
):
    """Returns all songs"""
    return pdb.query(SongModel).all()


@app.get("/api/v2/songs/{song_id}")
def get_song_by_id2(
    song_id: int,
    pdb: Session = Depends(get_db),
    _api_key: APIKey = Depends(get_api_key),
):
    """Returns a song by its id or 404 if not found"""
    # TODO: Add stream to song file ?
    return pdb.query(SongModel).filter(SongModel.id == song_id).first()


@app.post("/api/v2/songs/")
def post_song_v2(
    song: str,
    file: UploadFile,
    pdb: Session = Depends(get_db),
    _api_key: APIKey = Depends(get_api_key),
):
    """Creates a song and returns its id"""
    newSong = SongModel(name=song, artist_id="quack")
    pdb.add(newSong)
    pdb.commit()

    blob = bucket.blob(f"songs/{newSong.id}")
    blob.upload_from_file(file.file)

    return {"success": True, "created_id": newSong.id}
