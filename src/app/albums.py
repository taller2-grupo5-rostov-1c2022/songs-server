from src.exceptions import MessageException
from fastapi import APIRouter
from fastapi import Depends, File, UploadFile, Query

from src.firebase.access import get_bucket
from sqlalchemy.orm import Session
from src.database.access import get_db
from src.database import models
from src import roles, utils, schemas
from src.roles import get_role
from src.schemas import AlbumCreate, AlbumGet, AlbumUpdate

from src.schemas.pagination import CustomPage

router = APIRouter(tags=["albums"])


@router.get("/albums/", response_model=CustomPage[schemas.Album])
def get_albums(
    creator: str = None,
    role: roles.Role = Depends(get_role),
    artist: str = None,
    genre: str = None,
    name: str = None,
    pdb: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Returns all Albums"""
    albums = models.AlbumModel.search(
        pdb,
        role=role,
        creator_id=creator,
        artist=artist,
        genre=genre,
        name=name,
        limit=limit,
        offset=offset,
    )

    return albums


@router.get("/my_albums/", response_model=CustomPage[schemas.Album])
def get_my_albums(
    uid: str = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):

    albums = models.AlbumModel.search(
        pdb, role=roles.Role.admin(), creator_id=uid, limit=limit, offset=offset
    )

    return albums


@router.get("/albums/{album_id}", response_model=AlbumGet)
def get_album_by_id(
    album: models.AlbumModel = Depends(utils.album.get_album),
):
    """Returns an album by its id or 404 if not found"""

    return album


@router.post("/albums/", response_model=AlbumGet)
def post_album(
    album_create: AlbumCreate = Depends(utils.album.retrieve_album),
    cover: UploadFile = File(...),
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Creates an album and returns its id. Songs_ids form is encoded like '["song_id_1", "song_id_2", ...]'"""
    album = models.AlbumModel.create(
        pdb, **album_create.dict(), role=role, file=cover.file, bucket=bucket
    )

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
        raise MessageException(
            status_code=403,
            detail=f"User {uid} attempted to edit album of user with ID {album.creator_id}",
        )

    album_update = album_update.dict(exclude_none=True)
    if cover is not None:
        album.update(pdb, **album_update, file=cover.file, bucket=bucket, role=role)
    else:
        album.update(pdb, **album_update, role=role)


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
        raise MessageException(
            status_code=403,
            detail=f"User '{uid} attempted to delete album of user with ID {album.creator_id}",
        )

    album.delete(pdb, bucket=bucket)
