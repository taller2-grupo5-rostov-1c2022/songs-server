from src.constants import SUPPRESS_BLOB_ERRORS
from fastapi import APIRouter
from fastapi import Depends, File, HTTPException, UploadFile

from src.firebase.access import get_bucket
from typing import List
from sqlalchemy.orm import Session
from src.database.access import get_db
from src.database import models, crud
from src import roles, utils
from src.roles import get_role
from src.schemas.album.get import AlbumGet
from src.schemas.album.post import AlbumPost
from src.schemas.album.update import AlbumUpdate

router = APIRouter(tags=["albums"])


@router.get("/albums/", response_model=List[AlbumGet])
def get_albums(
    creator: str = None,
    role: roles.Role = Depends(get_role),
    artist: str = None,
    genre: str = None,
    name: str = None,
    pdb: Session = Depends(get_db),
):
    """Returns all Albums"""

    albums = crud.album.get_albums(
        pdb,
        role.can_see_blocked(),
        role.can_see_blocked(),
        creator,
        artist,
        genre,
        name,
    )

    albums = list(filter(None, albums))

    for album in albums:
        album.cover = utils.album.cover_url(album)
        album.score = utils.album.calculate_score(pdb, album)
        album.scores_amount = utils.album.calculate_scores_amount(pdb, album)

    return albums


@router.get("/my_albums/", response_model=List[AlbumGet])
def get_my_albums(
    uid: str = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
):

    albums = crud.album.get_albums(
        pdb, show_blocked_albums=True, show_blocked_songs=True, creator=uid
    )

    for album in albums:
        album.cover = utils.album.cover_url(album)
        album.score = utils.album.calculate_score(pdb, album)
        album.scores_amount = utils.album.calculate_scores_amount(pdb, album)

    return albums


@router.get("/albums/{album_id}", response_model=AlbumGet)
def get_album_by_id(
    album: models.AlbumModel = Depends(utils.album.get_album),
    pdb: Session = Depends(get_db),
):
    """Returns an album by its id or 404 if not found"""

    album.cover = utils.album.cover_url(album)
    album.score = utils.album.calculate_score(pdb, album)
    album.scores_amount = utils.album.calculate_scores_amount(pdb, album)

    return album


@router.post("/albums/", response_model=AlbumGet)
def post_album(
    album_post: AlbumPost = Depends(utils.album.retrieve_album),
    cover: UploadFile = File(...),
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Creates an album and returns its id. Songs_ids form is encoded like '["song_id_1", "song_id_2", ...]'"""
    album = crud.album.create_album(pdb, album_post, role.can_see_blocked())

    utils.album.upload_cover(pdb, bucket, album, cover.file, delete_if_fail=True)

    album.score = utils.album.calculate_score(pdb, album)
    album.scores_amount = utils.album.calculate_scores_amount(pdb, album)
    album.cover = utils.album.cover_url(album)
    return album


@router.put("/albums/{album_id}")
def update_album(
    album: models.AlbumModel = Depends(utils.album.get_album),
    uid: str = Depends(utils.user.retrieve_uid),
    role: roles.Role = Depends(get_role),
    album_update: AlbumUpdate = Depends(utils.album.retrieve_album_update),
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

    crud.album.update_album(
        pdb, album, album_update, role.can_see_blocked(), role.can_see_blocked()
    )

    if cover is not None:
        utils.album.upload_cover(pdb, bucket, album, cover.file, delete_if_fail=False)


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
    try:
        bucket.blob(f"covers/{album.id}").delete()
    except Exception as entry_not_found:
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507, detail=f"Could not delete cover for album {album.id}"
            ) from entry_not_found

    crud.album.delete_album(pdb, album)
