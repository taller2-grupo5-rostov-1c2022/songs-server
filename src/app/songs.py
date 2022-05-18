import datetime

from src import roles
from src.constants import STORAGE_PATH, SUPPRESS_BLOB_ERRORS
from src.postgres import schemas
from typing import List
from fastapi import APIRouter
from fastapi import Depends, File, HTTPException, UploadFile
from src.repositories import songs_repository as crud_songs
from src.firebase.access import get_bucket
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres.models import SongModel, ArtistModel
from src.repositories.resources_repository import (
    retrieve_song,
    retrieve_uid,
    retrieve_song_update,
)
from src.roles import get_role

router = APIRouter(tags=["songs"])


def create_song_artists_models(artists_names: List[str]):
    artists = []
    for artist_name in artists_names:
        artists.append(ArtistModel(name=artist_name))
    return artists


@router.get("/songs/", response_model=List[schemas.SongBase])
def get_songs(
    creator: str = None,
    role: roles.Role = Depends(get_role),
    artist: str = None,
    genre: str = None,
    sub_level: int = None,
    pdb: Session = Depends(get_db),
):
    """Returns all songs"""

    return crud_songs.get_songs(pdb, role, creator, artist, genre, sub_level)


@router.get("/songs/{song_id}", response_model=schemas.SongGet)
def get_song_by_id(
    song_id: int,
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
):
    """Returns a song by its id or 404 if not found"""
    song = crud_songs.get_song_by_id(pdb, role, song_id)

    song.file = (
        STORAGE_PATH + "songs/" + str(song_id) + "?t=" + str(song.file_last_update)
    )

    return song


@router.put("/songs/{song_id}")
def update_song(
    song_id: str,
    uid: str = Depends(retrieve_uid),
    role: roles.Role = Depends(get_role),
    song_update: schemas.SongUpdate = Depends(retrieve_song_update),
    file: UploadFile = None,
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Updates song by its id"""

    # even though id is an integer, we can compare with a string
    song = pdb.get(SongModel, song_id)
    if song is None:
        raise HTTPException(status_code=404, detail=f"Song '{song_id}' not found")
    if song.creator_id != uid and not role.can_edit_everything():
        raise HTTPException(
            status_code=403,
            detail=f"User '{uid} attempted to edit song of user with ID {song.creator_id}",
        )

    song_update = song_update.dict()

    for song_attr in song_update:
        if song_update[song_attr] is not None:
            setattr(song, song_attr, song_update[song_attr])
    if song_update["artists_names"] is not None:
        song.artists = create_song_artists_models(song_update["artists_names"])

    if song_update["blocked"] is not None:
        if not role.can_block():
            raise HTTPException(
                status_code=403,
                detail=f"User {uid} without permissions tried to block song {song.id}",
            )
        song.blocked = song_update["blocked"]

    pdb.commit()

    if file is not None:
        try:
            blob = bucket.blob("songs/" + song_id)
            blob.upload_from_file(file.file)
            song.file_last_update = datetime.datetime.now()
        except:  # noqa: W0707 # Want to catch all exceptions
            if not SUPPRESS_BLOB_ERRORS:
                raise HTTPException(
                    status_code=507, detail=f"Files for Song '{song_id}' not found"
                )

    pdb.commit()


@router.post("/songs/", response_model=schemas.SongBase)
def post_song(
    song_info: schemas.SongPost = Depends(retrieve_song),
    file: UploadFile = File(...),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Creates a song and returns its id. Artists form is encoded like '["artist1", "artist2", ...]'"""

    new_song = SongModel(
        **song_info.dict(exclude={"artists_names"}),
        artists=create_song_artists_models(song_info.artists_names),
        file_last_update=datetime.datetime.now(),
    )
    pdb.add(new_song)

    try:
        blob = bucket.blob(f"songs/{new_song.id}")
        blob.upload_from_file(file.file)
        blob.make_public()
    except:  # noqa: W0707 # Want to catch all exceptions
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507,
                detail=f"Could not upload Files for new Song {new_song.id}",
            )

    # Changes to the db should not be committed if there is an error
    # uploading the file
    pdb.commit()
    pdb.refresh(new_song)

    return new_song


@router.delete("/songs/{song_id}")
def delete_song(
    song_id: str,
    uid: str = Depends(retrieve_uid),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Deletes a song by its id"""

    song = pdb.query(SongModel).filter(SongModel.id == song_id).first()
    if song is None:
        raise HTTPException(status_code=404, detail=f"Song '{song_id}' not found")

    if uid != song.creator_id:
        raise HTTPException(
            status_code=403,
            detail=f"User with ID {uid} attempted to delete song of creator with ID {song.creator_id}",
        )

    pdb.query(SongModel).filter(SongModel.id == song_id).delete()
    pdb.commit()

    try:
        bucket.blob("songs/" + song_id).delete()
    except:  # noqa: W0707 # Want to catch all exceptions
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507, detail=f"Could not delete Song {song_id}"
            )

    return {"song_id": song_id}


@router.get("/my_songs/", response_model=List[schemas.SongBase])
def get_my_songs(uid: str = Depends(retrieve_uid), pdb: Session = Depends(get_db)):
    return crud_songs.get_songs(pdb, roles.Role.admin(), uid)
