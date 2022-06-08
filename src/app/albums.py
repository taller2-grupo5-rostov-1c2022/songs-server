import datetime
from src.postgres import schemas
from src.constants import SUPPRESS_BLOB_ERRORS
from fastapi import APIRouter
from fastapi import Depends, File, HTTPException, UploadFile
from src.firebase.access import get_bucket
from typing import List
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres import models
from src import roles
from src.repositories import album_utils, user_utils
from src.roles import get_role

router = APIRouter(tags=["albums"])


@router.get("/albums/", response_model=List[schemas.AlbumGet])
def get_albums(
    creator: str = None,
    role: roles.Role = Depends(get_role),
    artist: str = None,
    genre: str = None,
    sub_level: int = None,
    name: str = None,
    pdb: Session = Depends(get_db),
):
    """Returns all Albums"""

    albums = album_utils.get_albums(pdb, role, creator, artist, genre, sub_level, name)

    albums = list(filter(None, albums))

    for album in albums:
        album.cover = album_utils.cover_url(album)
        album.score = album_utils.calculate_score(pdb, album)
        album.scores_amount = album_utils.calculate_scores_amount(pdb, album)

    return albums


@router.get("/my_albums/", response_model=List[schemas.AlbumGet])
def get_my_albums(
    uid: str = Depends(user_utils.retrieve_uid),
    pdb: Session = Depends(get_db),
):

    albums = album_utils.get_albums(pdb, roles.Role.admin(), uid)

    for album in albums:
        album.cover = album_utils.cover_url(album)
        album.score = album_utils.calculate_score(pdb, album)
        album.scores_amount = album_utils.calculate_scores_amount(pdb, album)

    return albums


@router.get("/albums/{album_id}", response_model=schemas.AlbumGet)
def get_album_by_id(
    album: models.AlbumModel = Depends(album_utils.get_album),
    pdb: Session = Depends(get_db),
):
    """Returns an album by its id or 404 if not found"""

    album.cover = album_utils.cover_url(album)
    album.score = album_utils.calculate_score(pdb, album)
    album.scores_amount = album_utils.calculate_scores_amount(pdb, album)

    return album


@router.post("/albums/", response_model=schemas.AlbumGet)
def post_album(
    uid: str = Depends(user_utils.retrieve_uid),
    role: roles.Role = Depends(get_role),
    album_info: schemas.AlbumPost = Depends(album_utils.retrieve_album),
    cover: UploadFile = File(...),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Creates an album and returns its id. Songs_ids form is encoded like '["song_id_1", "song_id_2", ...]'"""

    album = models.AlbumModel(
        cover_last_update=datetime.datetime.now(),
        songs=[],
        **album_info.dict(exclude={"songs_ids"}),
    )

    pdb.add(album)
    pdb.commit()

    album_utils.update_songs(pdb, uid, role, album, album_info.songs_ids)
    album_utils.upload_cover(bucket, album, cover.file)

    pdb.add(album)
    pdb.commit()

    album.score = album_utils.calculate_score(pdb, album)
    album.scores_amount = album_utils.calculate_scores_amount(pdb, album)
    album.cover = album_utils.cover_url(album)
    return album


@router.put("/albums/{album_id}")
def update_album(
    album: models.AlbumModel = Depends(album_utils.get_album),
    uid: str = Depends(user_utils.retrieve_uid),
    role: roles.Role = Depends(get_role),
    album_update: schemas.AlbumUpdate = Depends(album_utils.retrieve_album_update),
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
        album_utils.update_songs(pdb, uid, role, album, album_update["songs_ids"])

    if album_update["blocked"] is not None:
        if not role.can_block():
            raise HTTPException(
                status_code=403,
                detail=f"User {uid} without permissions tried to block album {album.id}",
            )
        album.blocked = album_update["blocked"]

    if cover is not None:
        album_utils.upload_cover(bucket, album, cover.file)

    pdb.commit()


@router.delete("/albums/{album_id}")
def delete_album(
    album: models.AlbumModel = Depends(album_utils.get_album),
    uid: str = Depends(user_utils.retrieve_uid),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
    role: roles.Role = Depends(get_role),
):
    """Deletes an album by its id"""

    if uid != album.creator_id and not role.can_delete_everything():
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
    pdb.commit()
