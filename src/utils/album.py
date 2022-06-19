from src.database import models
from fastapi import HTTPException, Depends, status
from .. import roles, utils
import datetime
from src.constants import STORAGE_PATH
from src import schemas
from src.database.access import get_db
from typing import List, Optional
from sqlalchemy.orm import Session

from ..roles import get_role


def cover_url(album: models.AlbumModel):
    return (
        STORAGE_PATH
        + "covers/"
        + str(album.id)
        + "?t="
        + str(int(datetime.datetime.timestamp(album.file_last_update)))
    )


def calculate_scores_amount(pdb, album: models.AlbumModel):
    scores_amount = (
        pdb.query(models.AlbumModel)
        .join(models.ReviewModel.album)
        .filter(models.AlbumModel.id == album.id, models.ReviewModel.score != None)
        .count()
    )
    return scores_amount


def calculate_score(pdb, album: models.AlbumModel):
    scores_amount = calculate_scores_amount(pdb, album)
    if scores_amount == 0:
        return 0

    reviews = (
        pdb.query(models.ReviewModel.score)
        .join(models.ReviewModel.album)
        .filter(models.AlbumModel.id == album.id, models.ReviewModel.score != None)
        .all()
    )
    sum_scores = sum(review.score for review in reviews)

    return round(sum_scores / scores_amount, 1)


def get_album(
    album_id: int,
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
    uid: str = Depends(utils.user.retrieve_uid),
):
    return models.AlbumModel.get(pdb, _id=album_id, role=role, requester_id=uid)


def retrieve_album_update(
    resource_creator_update: schemas.ResourceCreatorUpdate = Depends(
        utils.resource.retrieve_resource_creator_update
    ),
    album: models.AlbumModel = Depends(get_album),
    songs_ids: Optional[List[int]] = Depends(utils.song.retrieve_songs_ids),
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
    uid: str = Depends(utils.user.retrieve_uid),
):
    validate_songs_for_album(album, songs_ids, uid, role, pdb)

    return schemas.AlbumUpdate(**resource_creator_update.dict(), songs_ids=songs_ids)


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
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only add songs you created",
                )
            if album is not None:
                if song.album_id is not None and song.album_id != album.id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You can only add songs that belong to the same album or none",
                    )


def retrieve_album(
    resource_creator: schemas.ResourceCreatorBase = Depends(
        utils.resource.retrieve_resource_creator
    ),
    songs_ids: Optional[List[int]] = Depends(utils.song.retrieve_songs_ids),
    pdb: Session = Depends(get_db),
    uid: str = Depends(utils.user.retrieve_uid),
    role: roles.Role = Depends(get_role),
):
    validate_songs_for_album(None, songs_ids, uid, role, pdb)

    return schemas.AlbumPost(**resource_creator.dict(), songs_ids=songs_ids)