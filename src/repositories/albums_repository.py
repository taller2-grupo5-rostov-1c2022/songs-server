from sqlalchemy.orm import Session, joinedload
from src.postgres.models import AlbumModel, ArtistModel, SongModel
from fastapi import HTTPException
from sqlalchemy import func
from .. import roles
from . import songs_repository as crud_songs
from typing import List, IO
import datetime
from src.constants import SUPPRESS_BLOB_ERRORS


def get_albums(
    pdb: Session,
    role: roles.Role,
    creator_id: str = None,
    artist: str = None,
    genre: str = None,
    sub_level: int = None,
):
    queries = []
    if not role.can_see_blocked():
        # This action should not be committed
        pdb.query(SongModel).filter(SongModel.blocked == True).delete()
        queries.append(AlbumModel.blocked == False)

    if creator_id is not None:
        queries.append(AlbumModel.creator_id == creator_id)
    if artist is not None:
        queries.append(func.lower(ArtistModel.name).contains(artist.lower()))
    if genre is not None:
        queries.append(func.lower(AlbumModel.genre).contains(genre.lower()))
    if sub_level is not None:
        queries.append(AlbumModel.sub_level == sub_level)

    results = (
        pdb.query(AlbumModel)
        .join(ArtistModel.songs, full=True)
        .join(SongModel.album, full=True)
        .filter(*queries)
        .all()
    )

    return results


def get_album_by_id(pdb: Session, role: roles.Role, album_id: int):
    queries = []
    if not role.can_see_blocked():
        # This action should not be committed
        pdb.query(SongModel).filter(SongModel.blocked == True).delete()
        queries.append(AlbumModel.blocked == False)

    album = (
        pdb.query(AlbumModel)
        .options(joinedload(AlbumModel.songs))
        .filter(AlbumModel.id == album_id)
        .first()
    )

    if album is None:
        raise HTTPException(
            status_code=404,
            detail=f"Album '{str(album_id)}' not found",
        )
    if album.blocked and not role.can_see_blocked():
        raise HTTPException(status_code=403, detail="Album is blocked")

    return album


def get_songs_list(pdb: Session, uid: str, role: roles.Role, songs_ids: List[int]):
    songs = []
    for song_id in songs_ids:
        song = crud_songs.get_song_by_id(pdb, role, song_id)
        if song.creator_id != uid:
            raise HTTPException(
                status_code=403,
                detail=f"User {uid} attempted to add song of another artist to its album",
            )

        if song.album is not None:
            raise HTTPException(
                status_code=403,
                detail=f"User {uid} attempted to add song to album but it was already in one",
            )
        songs.append(song)
    return songs


def set_cover(pdb: Session, bucket, album: AlbumModel, file: IO):
    try:
        blob = bucket.blob("covers/" + str(album.id))
        blob.upload_from_file(file)
        blob.make_public()
        album.cover_last_update = datetime.datetime.now() + datetime.timedelta(
            seconds=1
        )
        pdb.commit()
    except Exception as entry_not_found:
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507,
                detail=f"Could not upload cover for album {album.id}",
            ) from entry_not_found
