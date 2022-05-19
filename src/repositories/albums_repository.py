from sqlalchemy.orm import Session, contains_eager
from src.postgres.models import AlbumModel, ArtistModel, SongModel, CommentModel
from fastapi import HTTPException
from sqlalchemy import func
from .. import roles
from . import songs_repository as crud_songs
from typing import List, IO
import datetime
from src.constants import SUPPRESS_BLOB_ERRORS, STORAGE_PATH
from sqlalchemy import and_


def get_albums(
    pdb: Session,
    role: roles.Role,
    creator_id: str = None,
    artist: str = None,
    genre: str = None,
    sub_level: int = None,
):
    artist_queries = []
    album_queries = []
    join_conditions = [SongModel.album_id == AlbumModel.id]

    if not role.can_see_blocked():
        join_conditions.append(SongModel.blocked == False)
        album_queries.append(AlbumModel.blocked == False)

    if creator_id is not None:
        album_queries.append(AlbumModel.creator_id == creator_id)
    if artist is not None:
        artist_queries.append(func.lower(ArtistModel.name).contains(artist.lower()))
    if genre is not None:
        album_queries.append(func.lower(AlbumModel.genre).contains(genre.lower()))
    if sub_level is not None:
        album_queries.append(AlbumModel.sub_level == sub_level)

    results = (
        pdb.query(AlbumModel)
        .join(SongModel, and_(*join_conditions), full=True)
        .filter(*album_queries)
    )

    if artist is not None:
        results = results.join(
            ArtistModel, SongModel.artists.any(criterion=and_(True, *artist_queries))
        )

    return results.all()


def get_album_by_id(pdb: Session, role: roles.Role, album_id: int):
    join_conditions = [SongModel.album_id == AlbumModel.id]

    if not role.can_see_blocked():
        join_conditions.append(SongModel.blocked == False)

    albums = (
        pdb.query(AlbumModel)
        .options(contains_eager("songs"))
        .join(SongModel, and_(*join_conditions), full=True)
        .filter(AlbumModel.id == album_id)
        .all()
    )

    if len(albums) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Album '{str(album_id)}' not found",
        )
    album = albums[0]
    if album.blocked and not role.can_see_blocked():
        raise HTTPException(status_code=403, detail="Album is blocked")

    return album


def update_songs(
    pdb: Session, uid: str, role: roles.Role, album: AlbumModel, songs_ids: List[int]
):
    songs = []
    for song_id in songs_ids:
        song = crud_songs.get_song_by_id(pdb, role, song_id)
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


def upload_cover(bucket, album: AlbumModel, file: IO):
    try:
        blob = bucket.blob("covers/" + str(album.id))
        blob.upload_from_file(file)
        blob.make_public()
        album.cover_last_update = datetime.datetime.now() + datetime.timedelta(
            seconds=1
        )
    except Exception as entry_not_found:
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507,
                detail=f"Could not upload cover for album {album.id}",
            ) from entry_not_found


def cover_url(album: AlbumModel):
    return (
        STORAGE_PATH + "covers/" + str(album.id) + "?t=" + str(album.cover_last_update)
    )


def calculate_scores_amount(pdb: Session, album: AlbumModel):
    scores_amount = (
        pdb.query(AlbumModel)
        .join(CommentModel.album)
        .filter(AlbumModel.id == album.id, CommentModel.score != None)
        .count()
    )
    return scores_amount


def calculate_score(pdb: Session, album: AlbumModel):
    scores_amount = calculate_scores_amount(pdb, album)
    if scores_amount == 0:
        return 0

    comments = (
        pdb.query(CommentModel.score)
        .join(CommentModel.album)
        .filter(AlbumModel.id == album.id, CommentModel.score != None)
        .all()
    )
    sum_scores = sum(comment.score for comment in comments)

    return sum_scores / scores_amount


def get_comment_by_uid(pdb: Session, role: roles.Role, album: AlbumModel, uid: str):
    if album.blocked and not role.can_see_blocked():
        raise HTTPException(status_code=403, detail="Album is blocked")

    comment = pdb.query(CommentModel).filter(CommentModel.commenter_id == uid).first()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment
