import datetime

from src import roles
from src.constants import STORAGE_PATH, SUPPRESS_BLOB_ERRORS
from src.postgres import schemas
from typing import List, Optional
from fastapi import APIRouter, Header
from fastapi import Depends, File, Form, HTTPException, UploadFile
import json
from src.repositories import songs_repository as crud_songs
from src.firebase.access import get_bucket
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres.models import SongModel, UserModel, ArtistModel
from src.repositories.utils import ROLES_TABLE
from src.roles import get_role

router = APIRouter(tags=["songs"])


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
    uid: str = Header(...),
    role: roles.Role = Depends(get_role),
    name: str = Form(None),
    description: str = Form(None),
    genre: str = Form(None),
    artists: str = Form(None),
    sub_level: int = Form(None),
    file: UploadFile = None,
    blocked: Optional[bool] = Form(None),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Updates song by its id"""

    # even though id is an integer, we can compare with a string
    song = pdb.query(SongModel).filter(SongModel.id == song_id).first()
    if song is None:
        raise HTTPException(status_code=404, detail=f"Song '{song_id}' not found")
    if song.creator_id != uid and not role.can_edit_everything():
        raise HTTPException(
            status_code=403,
            detail=f"User '{uid} attempted to edit song of user with ID {song.creator_id}",
        )

    if name is not None:
        song.name = name
    if description is not None:
        song.description = description
    if genre is not None:
        song.genre = genre
    if sub_level is not None:
        song.sub_level = sub_level
    if blocked is not None:
        if not role.can_block():
            raise HTTPException(status_code=403, detail=f"User {uid} without permissions tried to block song {song.id}")
        song.blocked = blocked
    if artists is not None:
        artists_list = []
        try:
            parsed_artists = json.loads(artists)
            if len(parsed_artists) == 0:
                raise ValueError
            for artist_name in json.loads(artists):
                artists_list.append(ArtistModel(name=artist_name))
            song.artists = artists_list

        except ValueError as e:
            raise HTTPException(
                status_code=422, detail="Artists string is not well encoded"
            ) from e

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

    return schemas.SongResponse(success=True, id=song.id if song else song_id)


@router.post("/songs/")
def post_song(
    uid: str = Header(...),
    name: str = Form(...),
    description: str = Form(...),
    artists: str = Form(...),
    genre: str = Form(...),
    sub_level: int = Form(None),
    file: UploadFile = File(...),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Creates a song and returns its id. Artists form is encoded like '["artist1", "artist2", ...]'"""

    # The user is not in the database
    if not pdb.query(UserModel).filter(UserModel.id == uid).all():
        raise HTTPException(status_code=403, detail=f"User with ID {uid} not found")

    artists_models = []
    try:
        parsed_artists = json.loads(artists)
        if len(parsed_artists) == 0:
            raise ValueError
        for artist_name in parsed_artists:
            artists_models.append(ArtistModel(name=artist_name))
    except ValueError as e:
        raise HTTPException(
            status_code=422, detail="Artists string is not well encoded"
        ) from e

    if sub_level is None:
        sub_level = 0

    new_song = SongModel(
        name=name,
        description=description,
        creator_id=uid,
        artists=artists_models,
        genre=genre,
        sub_level=sub_level,
        blocked=False,
        file_last_update=datetime.datetime.now(),
    )
    pdb.add(new_song)
    pdb.commit()
    pdb.refresh(new_song)

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

    return schemas.SongResponse(
        success=True,
        id=new_song.id,
        file=STORAGE_PATH
        + "songs/"
        + str(new_song.id)
        + "?t="
        + str(new_song.file_last_update),
    )


@router.delete("/songs/{song_id}")
def delete_song(
    song_id: str,
    uid: str = Header(...),
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
def get_my_songs(uid: str = Header(...), pdb: Session = Depends(get_db)):
    return crud_songs.get_songs(pdb, roles.Role.admin(), uid)
