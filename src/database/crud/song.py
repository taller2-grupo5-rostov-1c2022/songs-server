from fastapi import HTTPException, status
import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from src import schemas
from src.database import models


def create_song(pdb: Session, song_info: schemas.SongPost):

    new_song = models.SongModel(
        **song_info.dict(exclude={"artists_names"}),
        artists=create_song_artists_models(song_info.artists_names),
        file_last_update=datetime.datetime.now(),
    )
    pdb.add(new_song)
    pdb.commit()

    return new_song


def delete_song(pdb: Session, song: models.SongModel):
    pdb.delete(song)
    pdb.commit()


def get_songs(
    pdb: Session,
    show_blocked_songs: bool,
    creator_id: str = None,
    artist: str = None,
    genre: str = None,
    sub_level: int = None,
    name: str = None,
):
    queries = []
    if not show_blocked_songs:
        queries.append(models.SongModel.blocked == False)

    if creator_id is not None:
        queries.append(models.SongModel.creator_id == creator_id)
    if artist is not None:
        queries.append(func.lower(models.ArtistModel.name).contains(artist.lower()))
    if genre is not None:
        queries.append(func.lower(models.SongModel.genre).contains(genre.lower()))
    if sub_level is not None:
        queries.append(models.SongModel.sub_level == sub_level)
    if name is not None:
        queries.append(func.lower(models.SongModel.name).contains(name.lower()))

    return (
        pdb.query(models.SongModel)
        .join(models.ArtistModel.songs)
        .filter(*queries)
        .all()
    )


def get_songs_by_id(
    pdb: Session, songs_ids: List[int], show_blocked_songs: bool
) -> List[models.SongModel]:
    songs = []
    for song_id in songs_ids:
        song = get_song_by_id(pdb, show_blocked_songs, song_id)
        songs.append(song)

    return songs


def get_song_by_id(pdb: Session, show_blocked_songs, song_id: int) -> models.SongModel:
    filters = [song_id == models.SongModel.id]
    if not show_blocked_songs:
        filters.append(models.SongModel.blocked == False)

    song = (
        pdb.query(models.SongModel)
        .join(models.ArtistModel.songs)
        .filter(*filters)
        .first()
    )
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Song not found"
        )
    return song


def create_song_artists_models(artists_names: List[str]):
    artists = []
    for artist_name in artists_names:
        artists.append(models.ArtistModel(name=artist_name))
    return artists


def update_song(
    pdb: Session,
    song: models.SongModel,
    song_update: schemas.SongUpdate,
    can_block: bool,
):
    artist_names = song_update.artists_names
    song_update = song_update.dict(exclude_none=True, exclude={"artists_names"})

    for song_attr in song_update:
        setattr(song, song_attr, song_update[song_attr])

    if artist_names is not None:
        song.artists = create_song_artists_models(artist_names)

    if "blocked" in song_update and not can_block:
        raise ValueError

    pdb.commit()
