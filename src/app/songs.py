from src import roles, utils, schemas
from typing import List
from fastapi import APIRouter
from fastapi import Depends, File, HTTPException, UploadFile, status, Query

from src.firebase.access import get_bucket
from sqlalchemy.orm import Session
from src.database.access import get_db
from src.database import models
from src.roles import get_role

router = APIRouter(tags=["songs"])


@router.get("/songs/", response_model=List[schemas.SongBase])
def get_songs(
    creator: str = None,
    role: roles.Role = Depends(get_role),
    artist: str = None,
    genre: str = None,
    sub_level: int = None,
    name: str = None,
    pdb: Session = Depends(get_db),
    page: int = Query(0, ge=0),
    size: int = Query(50, ge=1, le=100),
):
    """Returns all songs"""

    songs = models.SongModel.search(
        pdb,
        role=role,
        creator_id=creator,
        artist=artist,
        genre=genre,
        sub_level=sub_level,
        name=name,
        page=page,
        size=size,
    )

    return songs


@router.get("/songs/{song_id}", response_model=schemas.SongGet)
def get_song_by_id(
    song: models.SongModel = Depends(utils.song.get_song),
    bucket=Depends(get_bucket),
):
    """Returns a song by its id or 404 if not found"""

    song.file = song.url(bucket)

    return song


@router.put("/songs/{song_id}")
def update_song(
    song: models.SongModel = Depends(utils.song.get_song),
    uid: str = Depends(utils.user.retrieve_uid),
    role: roles.Role = Depends(get_role),
    song_update: schemas.SongUpdate = Depends(utils.song.retrieve_song_update),
    file: UploadFile = None,
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Updates song by its id"""

    if song.creator_id != uid and not role.can_edit_everything():
        raise HTTPException(
            status_code=403,
            detail=f"User '{uid} attempted to edit song of user with ID {song.creator_id}",
        )

    if file is not None:
        song.update(
            pdb,
            **song_update.dict(exclude_none=True),
            role=role,
            file=file.file,
            bucket=bucket,
        )
    else:
        song.update(pdb, **song_update.dict(exclude_none=True), role=role)


@router.post("/songs/", response_model=schemas.SongBase)
def post_song(
    song_create: schemas.SongCreate = Depends(utils.song.retrieve_song),
    file: UploadFile = File(...),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Creates a song and returns its id. Artists form is encoded like '["artist1", "artist2", ...]'"""
    new_song = models.SongModel.create(
        pdb, **song_create.dict(), bucket=bucket, file=file.file
    )

    return new_song


@router.delete("/songs/{song_id}")
def delete_song(
    song: models.SongModel = Depends(utils.song.get_song),
    uid: str = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
    role: roles.Role = Depends(get_role),
):
    """Deletes a song by its id"""

    if song.creator_id != uid and not role.can_delete_everything():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User '{uid} attempted to delete song of user with ID {song.creator_id}",
        )

    song.delete(pdb, bucket=bucket, role=role)


@router.get("/my_songs/", response_model=List[schemas.SongBase])
def get_my_songs(
    uid: str = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
    page: int = Query(0, ge=0),
    size: int = Query(50, ge=1, le=100),
):
    return models.SongModel.search(
        pdb, creator_id=uid, role=roles.Role.admin(), page=page, size=size
    )
