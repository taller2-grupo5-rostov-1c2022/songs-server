from sqlalchemy.orm import contains_eager
from src.postgres import models
from fastapi import HTTPException, Depends, Form
from sqlalchemy import func
from .. import roles
from typing import IO
import datetime
from src.constants import SUPPRESS_BLOB_ERRORS, STORAGE_PATH
from sqlalchemy import and_
from src.repositories import resource_utils, song_utils, artist_utils
from ..postgres import schemas
from ..postgres.database import get_db
from typing import List, Optional
from sqlalchemy.orm import Session
from ..roles import get_role


def get_albums(
    pdb: Session = Depends(get_db),
    role: roles.Role = Depends(get_role),
    creator: str = None,
    artist: str = None,
    genre: str = None,
    name: str = None,
):
    join_conditions = [models.SongModel.album_id == models.AlbumModel.id]
    filters = []

    if not role.can_see_blocked():
        join_conditions.append(models.SongModel.blocked == False)
        filters.append(models.AlbumModel.blocked == False)

    if creator is not None:
        filters.append(models.AlbumModel.creator_id == creator)
    if artist is not None:
        filters.append(
            models.SongModel.artists.any(
                func.lower(models.ArtistModel.name).contains(artist.lower())
            )
        )

    if genre is not None:
        filters.append(func.lower(models.AlbumModel.genre).contains(genre.lower()))
    if name is not None:
        filters.append(func.lower(models.AlbumModel.name).contains(name.lower()))

    albums = (
        pdb.query(models.AlbumModel)
        .options(contains_eager("songs"))
        .join(models.SongModel, and_(*join_conditions), full=True)
        .filter(and_(True, *filters))
        .all()
    )

    return albums


def get_album_by_id(pdb, role: roles.Role, album_id: int):
    join_conditions = [models.SongModel.album_id == models.AlbumModel.id]
    filters = [album_id == models.AlbumModel.id]

    if not role.can_see_blocked():
        join_conditions.append(models.SongModel.blocked == False)
        filters.append(models.AlbumModel.blocked == False)

    album = (
        pdb.query(models.AlbumModel)
        .options(contains_eager("songs"))
        .join(models.SongModel, and_(*join_conditions), full=True)
        .filter(and_(True, *filters))
        .all()
    )
    if len(album) == 0:
        raise HTTPException(
            status_code=404,
            detail="Album not found",
        )
    return album[0]


def update_songs(
    pdb, uid: str, role: roles.Role, album: models.AlbumModel, songs_ids: List[int]
):
    songs = []
    for song_id in songs_ids:
        song = song_utils.get_song_by_id(pdb, role, song_id)
        if song.creator_id != uid:
            raise HTTPException(
                status_code=403,
                detail=f"User {uid} attempted to add song of another artist to its album",
            )

        if song.album is not None and song.album != album:
            raise HTTPException(
                status_code=403,
                detail=f"User {uid} attempted to add song to album but it was already in one",
            )
        songs.append(song)
    album.songs = songs


def upload_cover(bucket, album: models.AlbumModel, file: IO):
    try:
        blob = bucket.blob("covers/" + str(album.id))
        blob.upload_from_file(file)
        blob.make_public()
        album.cover_last_update = datetime.datetime.now()
    except Exception as entry_not_found:
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507,
                detail=f"Could not upload cover for album {album.id}",
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


def get_review_by_uid(pdb, role: roles.Role, album: models.AlbumModel, uid: str):
    if album.blocked and not role.can_see_blocked():
        raise HTTPException(status_code=403, detail="Album is blocked")

    review = (
        pdb.query(models.ReviewModel)
        .filter(
            models.ReviewModel.reviewer_id == uid,
            models.ReviewModel.album_id == album.id,
        )
        .first()
    )

    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


def get_album(
    album_id: int, role: roles.Role = Depends(get_role), pdb: Session = Depends(get_db)
):
    return get_album_by_id(pdb, role, album_id)


def retrieve_album_update(
    resource_creator_update: schemas.ResourceCreatorUpdate = Depends(
        resource_utils.retrieve_resource_creator_update
    ),
    songs_ids: List[int] = Depends(song_utils.retrieve_songs_ids),
):
    return schemas.AlbumUpdate(songs_ids=songs_ids, **resource_creator_update.dict())


def retrieve_album(
    resource_creator: schemas.ResourceCreatorBase = Depends(
        resource_utils.retrieve_resource_creator
    ),
    songs_ids: List[int] = Depends(song_utils.retrieve_songs_ids),
):
    return schemas.AlbumPost(songs_ids=songs_ids, **resource_creator.dict())


def retrieve_album_info(album: Optional[int] = Form(None), pdb=Depends(get_db)):
    if album is not None:
        album_id = album
        album = pdb.get(models.AlbumModel, album_id)
        if album is None:
            raise HTTPException(status_code=404, detail="Album not found")
    return album


def retrieve_song(
    resource_creator: schemas.ResourceCreatorBase = Depends(
        resource_utils.retrieve_resource_creator
    ),
    artists_names: List[str] = Depends(artist_utils.retrieve_artists_names),
    album_info: Optional[schemas.AlbumBase] = Depends(retrieve_album_info),
    sub_level: Optional[int] = Form(None),
):
    if sub_level is None:
        sub_level = 0
    return schemas.SongPost(
        artists_names=artists_names,
        album=album_info,
        sub_level=sub_level,
        **resource_creator.dict(),
    )
