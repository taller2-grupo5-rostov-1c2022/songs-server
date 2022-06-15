import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, contains_eager
from sqlalchemy.sql import and_, func

from src import schemas
from src.database import models
from .song import get_song_by_id, get_songs_by_id


def create_album(pdb: Session, album_post: schemas.AlbumPost, can_see_blocked: bool):
    new_album = models.AlbumModel(
        **album_post.dict(exclude={"songs_ids"}),
        cover_last_update=datetime.datetime.now(),
        songs=[],
    )

    for song_id in album_post.songs_ids:
        song = get_song_by_id(pdb, can_see_blocked, song_id)
        new_album.songs.append(song)

    pdb.add(new_album)
    pdb.commit()

    return new_album


def update_album(
    pdb: Session,
    album: models.AlbumModel,
    album_update: schemas.AlbumUpdate,
    can_block: bool,
    show_blocked_songs: bool,
):
    blocked = album_update.blocked
    songs_ids = album_update.songs_ids
    album_update = album_update.dict(
        exclude_none=True, exclude={"blocked", "songs_ids"}
    )

    for album_attr in album_update:
        setattr(album, album_attr, album_update[album_attr])
    if songs_ids is not None:
        album.songs = get_songs_by_id(pdb, songs_ids, show_blocked_songs)

    if blocked:
        if not can_block:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You can't block albums"
            )

        album.blocked = blocked

    pdb.commit()


def get_album_by_id(
    pdb: Session, album_id: int, show_blocked_albums: bool, show_blocked_songs: bool
):
    join_conditions = [models.SongModel.album_id == models.AlbumModel.id]
    filters = [album_id == models.AlbumModel.id]

    if not show_blocked_songs:
        join_conditions.append(models.SongModel.blocked == False)
    if not show_blocked_albums:
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Album not found"
        )
    return album[0]


def get_albums(
    pdb: Session,
    show_blocked_albums: bool,
    show_blocked_songs: bool,
    creator: str = None,
    artist: str = None,
    genre: str = None,
    name: str = None,
):
    join_conditions = [models.SongModel.album_id == models.AlbumModel.id]
    filters = []

    if not show_blocked_songs:
        join_conditions.append(models.SongModel.blocked == False)
    if not show_blocked_albums:
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


def delete_album(
    pdb: Session,
    album: models.AlbumModel,
):
    pdb.delete(album)
    pdb.commit()
