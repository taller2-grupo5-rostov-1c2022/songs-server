from src.database import models, crud
from fastapi import HTTPException, Depends, Form, status
from .. import roles, utils
from typing import IO
import datetime
from src.constants import SUPPRESS_BLOB_ERRORS, STORAGE_PATH
from src import schemas
from src.database.access import get_db
from typing import List, Optional
from sqlalchemy.orm import Session

from ..roles import get_role


def upload_cover(pdb, bucket, album: models.AlbumModel, file: IO, delete_if_fail: bool):
    try:
        blob = bucket.blob(f"covers/{album.id}")
        blob.upload_from_file(file)
        blob.make_public()
        album_update = schemas.AlbumUpdateCover(
            cover_last_update=datetime.datetime.now()
        )
        crud.album.update_album(pdb, album, album_update, False, False)
    except Exception as entry_not_found:
        if not SUPPRESS_BLOB_ERRORS:
            if delete_if_fail:
                crud.album.delete_album(pdb, album)
            raise HTTPException(
                status_code=507,
                detail=f"Could not upload cover for album {album.id}"
                + str(entry_not_found),
            ) from entry_not_found


def cover_url(album: models.AlbumModel):
    return (
        STORAGE_PATH
        + "covers/"
        + str(album.id)
        + "?t="
        + str(int(datetime.datetime.timestamp(album.cover_last_update)))
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
    album_id: int, role: roles.Role = Depends(get_role), pdb: Session = Depends(get_db)
):
    return crud.album.get_album_by_id(
        pdb, album_id, role.can_see_blocked(), role.can_see_blocked()
    )


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
            song = crud.song.get_song_by_id(pdb, role.can_see_blocked(), song_id)
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


def retrieve_album_from_form(
    album_id: Optional[int] = Form(None),
    pdb: Session = Depends(get_db),
    role: roles.Role = Depends(get_role),
):
    if album_id is None:
        return None

    album = crud.album.get_album_by_id(
        pdb, album_id, role.can_see_blocked(), role.can_see_blocked()
    )
    if album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    return album


def retrieve_song(
    resource_creator: schemas.ResourceCreatorBase = Depends(
        utils.resource.retrieve_resource_creator
    ),
    artists_names: List[str] = Depends(utils.artist.retrieve_artists_names),
    album: Optional[schemas.AlbumBase] = Depends(retrieve_album_from_form),
    sub_level: Optional[int] = Form(None),
):
    if album is not None:
        album = schemas.AlbumBase.from_orm(album)

    if sub_level is None:
        sub_level = 0
    return schemas.SongPost(
        artists_names=artists_names,
        album=album,
        sub_level=sub_level,
        **resource_creator.dict(),
    )
