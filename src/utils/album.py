from src.exceptions import MessageException
from src.database import models
from fastapi import Depends, status
from .. import roles, utils
from src import schemas
from src.database.access import get_db
from typing import List, Optional
from sqlalchemy.orm import Session

from ..roles import get_role


def get_album(
    album_id: int,
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
    uid: str = Depends(utils.user.retrieve_uid),
):
    return models.AlbumModel.get(pdb, _id=album_id, role=role, requester_id=uid)


def retrieve_album_update(
    album_update_collector: schemas.AlbumUpdateCollector = Depends(
        schemas.AlbumUpdateCollector.as_form
    ),
    album: models.AlbumModel = Depends(get_album),
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
    uid: str = Depends(utils.user.retrieve_uid),
):
    return schemas.AlbumUpdate(
        pdb, **album_update_collector.dict(), creator_id=uid, role=role, album=album
    )


def validate_songs_for_album(
    album: Optional[models.AlbumModel],
    songs_ids: List[int],
    uid: str,
    role: roles.Role,
    pdb: Session,
):
    if songs_ids is not None:
        for song_id in songs_ids:
            song = models.SongModel.get(pdb, _id=song_id, role=role)
            if song.creator_id != uid:
                raise MessageException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only add songs you created",
                )
            if album is not None:
                if song.album_id is not None and song.album_id != album.id:
                    raise MessageException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You can only add songs that belong to the same album or none",
                    )


def retrieve_album(
    album_create_collector: schemas.AlbumCreateCollector = Depends(
        schemas.AlbumCreateCollector.as_form
    ),
    pdb: Session = Depends(get_db),
    uid: str = Depends(utils.user.retrieve_uid),
    role: roles.Role = Depends(get_role),
):
    return schemas.AlbumCreate(
        pdb, **album_create_collector.dict(), creator_id=uid, role=role
    )
