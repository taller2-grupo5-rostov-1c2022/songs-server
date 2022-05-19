import datetime
from src.postgres import schemas
from src.postgres import models
from src.constants import STORAGE_PATH, SUPPRESS_BLOB_ERRORS
from fastapi import APIRouter
from fastapi import Depends, File, HTTPException, UploadFile
from src.firebase.access import get_bucket
from src.repositories import albums_repository as crud_albums
from typing import List, Optional
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres.models import AlbumModel, UserModel
from src import roles
from src.repositories.resources_repository import (
    retrieve_album_update,
    retrieve_album,
    retrieve_uid, get_album,
)
from src.roles import get_role

router = APIRouter(tags=["albums"])


@router.get("/albums/", response_model=List[schemas.AlbumGet])
def get_albums(
    creator: str = None,
    role: roles.Role = Depends(get_role),
    artist: str = None,
    genre: str = None,
    sub_level: int = None,
    pdb: Session = Depends(get_db),
):
    """Returns all Albums"""

    albums = crud_albums.get_albums(pdb, role, creator, artist, genre, sub_level)

    albums = list(filter(None, albums))

    for album in albums:

        album.cover = (
            STORAGE_PATH
            + "covers/"
            + str(album.id)
            + "?t="
            + str(album.cover_last_update)
        )

    return albums


@router.get("/my_albums/", response_model=List[schemas.AlbumGet])
def get_my_albums(
    uid: str = Depends(retrieve_uid),
    pdb: Session = Depends(get_db),
):

    albums = crud_albums.get_albums(pdb, roles.Role.admin(), uid)

    for album in albums:
        album.cover = (
            STORAGE_PATH
            + "covers/"
            + str(album.id)
            + "?t="
            + str(int(datetime.datetime.timestamp(album.cover_last_update)))
        )

    return albums


@router.get("/albums/{album_id}", response_model=schemas.AlbumGet)
def get_album_by_id(
    album: AlbumModel = Depends(get_album)
):
    """Returns an album by its id or 404 if not found"""

    album.cover = (
        STORAGE_PATH + "covers/" + str(album.id) + "?t=" + str(album.cover_last_update)
    )

    return album


@router.post("/albums/", response_model=schemas.AlbumBase)
def post_album(
    uid: str = Depends(retrieve_uid),
    role: roles.Role = Depends(get_role),
    album_info: schemas.AlbumPost = Depends(retrieve_album),
    cover: UploadFile = File(...),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Creates an album and returns its id. Songs_ids form is encoded like '["song_id_1", "song_id_2", ...]'"""
    creator = pdb.get(UserModel, uid)
    if creator is None:
        raise HTTPException(status_code=404, detail=f"User with id {uid} not found")

    album = models.AlbumModel(
        cover_last_update=datetime.datetime.now(),
        songs=[],
        creator=creator,
        **album_info.dict(exclude={"songs_ids"}),
    )
    crud_albums.update_songs(pdb, uid, role, album, album_info.songs_ids)

    pdb.add(album)

    crud_albums.set_cover(bucket, album, cover.file)
    pdb.commit()
    return album


@router.put("/albums/{album_id}")
def update_album(
    album: AlbumModel = Depends(get_album),
    uid: str = Depends(retrieve_uid),
    role: roles.Role = Depends(get_role),
    album_update: schemas.AlbumUpdate = Depends(retrieve_album_update),
    cover: UploadFile = File(None),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Updates album by its id"""

    if album.creator_id != uid and not role.can_edit_everything():
        raise HTTPException(
            status_code=403,
            detail=f"User {uid} attempted to edit album of user with ID {album.creator_id}",
        )

    album_update = album_update.dict()

    for album_attr in album_update:
        if album_update[album_attr] is not None:
            setattr(album, album_attr, album_update[album_attr])
    if album_update["songs_ids"] is not None:
        crud_albums.update_songs(pdb, uid, role, album, album_update["songs_ids"])

    if album_update["blocked"] is not None:
        if not role.can_block():
            raise HTTPException(
                status_code=403,
                detail=f"User {uid} without permissions tried to block album {album.id}",
            )
        album.blocked = album_update["blocked"]

    if cover is not None:
        crud_albums.set_cover(bucket, album, cover.file)

    pdb.commit()


@router.delete("/albums/{album_id}")
def delete_album(
    album: AlbumModel = Depends(get_album),
    uid: str = Depends(retrieve_uid),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Deletes an album by its id"""
    album = pdb.get(AlbumModel, album.id)
    if album is None:
        raise HTTPException(status_code=404, detail=f"Album '{album.id}' not found")

    if uid != album.creator_id:
        raise HTTPException(
            status_code=403,
            detail=f"User '{uid} attempted to delete album of user with ID {album.creator_id}",
        )
    pdb.delete(album)
    try:
        bucket.blob(f"covers/{album.id}").delete()
    except Exception as entry_not_found:
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507, detail=f"Could not delete cover for album {album.id}"
            ) from entry_not_found


@router.post("/albums/{album_id}/comments/")
def comment_album(
        album: AlbumModel = Depends(get_album),
        uid: str = Depends(retrieve_uid),
        text: Optional[str] = None,
        score: Optional[int] = None,
        pdb: Session = Depends(get_db)
):
    if text is None and score is None:
        raise HTTPException(status_code=422, detail="Text and score cannot be None at the same time")

    comments = album.comments



