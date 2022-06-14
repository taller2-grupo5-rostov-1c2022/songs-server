import datetime
from src.postgres import schemas
from src.constants import SUPPRESS_BLOB_ERRORS
from fastapi import APIRouter
from fastapi import Depends, File, HTTPException, UploadFile
from src.firebase.access import get_bucket
from typing import List
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.database import models
from src import roles, utils
from src.roles import get_role

router = APIRouter(tags=["albums"])


@router.get("/albums/", response_model=List[schemas.AlbumGet])
def get_albums(
    creator: str = None,
    role: roles.Role = Depends(get_role),
    artist: str = None,
    genre: str = None,
    name: str = None,
    pdb: Session = Depends(get_db),
):
    """Returns all Albums"""

    albums = utils.album.get_albums(pdb, role, creator, artist, genre, name)

    albums = list(filter(None, albums))

    for album in albums:
        album.cover = utils.album.cover_url(album)
        album.score = utils.album.calculate_score(pdb, album)
        album.scores_amount = utils.album.calculate_scores_amount(pdb, album)

    return albums


@router.get("/my_albums/", response_model=List[schemas.AlbumGet])
def get_my_albums(
    uid: str = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
):

    albums = utils.album.get_albums(pdb, roles.Role.admin(), uid)

    for album in albums:
        album.cover = utils.album.cover_url(album)
        album.score = utils.album.calculate_score(pdb, album)
        album.scores_amount = utils.album.calculate_scores_amount(pdb, album)

    return albums


@router.get("/albums/{album_id}", response_model=schemas.AlbumGet)
def get_album_by_id(
    album: models.AlbumModel = Depends(utils.album.get_album),
    pdb: Session = Depends(get_db),
):
    """Returns an album by its id or 404 if not found"""

    album.cover = utils.album.cover_url(album)
    album.score = utils.album.calculate_score(pdb, album)
    album.scores_amount = utils.album.calculate_scores_amount(pdb, album)

    return album


@router.post("/albums/", response_model=schemas.AlbumGet)
def post_album(
    uid: str = Depends(utils.user.retrieve_uid),
    role: roles.Role = Depends(get_role),
    album_info: schemas.AlbumPost = Depends(utils.album.retrieve_album),
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

    utils.album.update_songs(pdb, uid, role, album, album_info.songs_ids)
    utils.album.upload_cover(bucket, album, cover.file)

    pdb.add(album)
    pdb.commit()

    album.score = utils.album.calculate_score(pdb, album)
    album.scores_amount = utils.album.calculate_scores_amount(pdb, album)
    album.cover = utils.album.cover_url(album)
    return album


@router.put("/albums/{album_id}")
def update_album(
    album: models.AlbumModel = Depends(utils.album.get_album),
    uid: str = Depends(utils.user.retrieve_uid),
    role: roles.Role = Depends(get_role),
    album_update: schemas.AlbumUpdate = Depends(utils.album.retrieve_album_update),
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
        utils.album.update_songs(pdb, uid, role, album, album_update["songs_ids"])

    if album_update["blocked"] is not None:
        if not role.can_block():
            raise HTTPException(
                status_code=403,
                detail=f"User {uid} without permissions tried to block album {album.id}",
            )
        album.blocked = album_update["blocked"]

    if cover is not None:
        utils.album.upload_cover(bucket, album, cover.file)

    pdb.commit()


@router.delete("/albums/{album_id}")
def delete_album(
    album: models.AlbumModel = Depends(utils.album.get_album),
    uid: str = Depends(utils.user.retrieve_uid),
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
