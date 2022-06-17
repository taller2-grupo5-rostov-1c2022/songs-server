from typing import List

from sqlalchemy.orm import Session, contains_eager
from sqlalchemy.sql import and_
from fastapi import HTTPException, status

from src import schemas
from src.database import models
from src.database.models import (
    song_playlist_association_table,
    playlist_favorite_association_table,
)


def get_users(pdb: Session) -> List[models.UserModel]:
    return pdb.query(models.UserModel).all()


def create_user(pdb: Session, user_info: schemas.UserPostComplete) -> models.UserModel:
    uid = user_info.uid
    user_info = user_info.dict(exclude={"uid"})

    user = models.UserModel(
        **user_info,
        id=uid,
    )
    pdb.add(user)
    pdb.commit()
    return user


def delete_user(pdb: Session, user: models.UserModel):
    pdb.delete(user)
    pdb.commit()


def get_user_by_id(pdb: Session, uid: str) -> models.UserModel:
    colab = pdb.get(models.UserModel, uid)
    if colab is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {uid} not found",
        )
    return colab


def add_playlist_to_favorites(
    pdb: Session, user: models.UserModel, playlist: models.PlaylistModel
):
    if playlist in user.favorite_playlists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Playlist already in favorites",
        )
    user.favorite_playlists.append(playlist)
    pdb.commit()


def remove_playlist_from_favorites(
    pdb: Session, user: models.UserModel, playlist: models.PlaylistModel
):
    if playlist not in user.favorite_playlists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not in favorites",
        )
    user.favorite_playlists.remove(playlist)
    pdb.commit()


def get_favorite_playlists(
    pdb: Session,
    user: models.UserModel,
    show_blocked_playlists: bool,
    show_blocked_songs: bool,
) -> List[models.PlaylistModel]:
    filters = [models.UserModel.id == user.id]
    join_conditions = []
    if not show_blocked_playlists:
        filters.append(models.PlaylistModel.blocked == False)

    if not show_blocked_songs:
        join_conditions.append(models.SongModel.blocked == False)

    playlists = (
        pdb.query(models.PlaylistModel)
        .join(
            song_playlist_association_table,
            song_playlist_association_table.c.playlist_id == models.PlaylistModel.id,
            isouter=True,
        )
        .join(models.SongModel, and_(True, *join_conditions), isouter=True)
        .join(
            playlist_favorite_association_table,
            playlist_favorite_association_table.c.playlist_id
            == models.PlaylistModel.id,
        )
        .join(
            models.UserModel,
            playlist_favorite_association_table.c.user_id == models.UserModel.id,
        )
        .options(contains_eager("songs"))
        .filter(and_(*filters))
    ).all()

    playlists = [p for p in playlists if p is not None]

    return playlists


def add_album_to_favorites(
    pdb: Session, user: models.UserModel, album: models.AlbumModel
):
    if album in user.favorite_albums:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Album already in favorites",
        )
    user.favorite_albums.append(album)
    pdb.commit()


def remove_album_from_favorites(
    pdb: Session, user: models.UserModel, album: models.AlbumModel
):
    if album not in user.favorite_albums:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Album not in favorites",
        )
    user.favorite_albums.remove(album)
    pdb.commit()


def get_favorite_albums(
    user: models.UserModel, show_blocked_albums: bool, show_blocked_songs: bool
) -> List[models.AlbumModel]:
    join_conditions = [models.SongModel.album_id == models.AlbumModel.id]
    filters = []
    if not show_blocked_albums:
        filters.append(models.AlbumModel.blocked == False)

    if not show_blocked_songs:
        join_conditions.append(models.SongModel.blocked == False)

    albums = (
        user.favorite_albums.options(contains_eager("songs"))
        .join(models.SongModel, and_(*join_conditions), full=True)
        .filter(models.AlbumModel.blocked == False)
        .distinct(models.AlbumModel.id)
        .all()
    )
    return albums


def add_song_to_favorites(pdb: Session, user: models.UserModel, song: models.SongModel):
    if song in user.favorite_songs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Song already in favorites",
        )
    user.favorite_songs.append(song)
    pdb.commit()


def remove_song_from_favorites(
    pdb: Session, user: models.UserModel, song: models.SongModel
):
    if song not in user.favorite_songs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not in favorites",
        )
    user.favorite_songs.remove(song)
    pdb.commit()


def get_favorite_songs(
    user: models.UserModel, show_blocked_songs: bool
) -> List[models.SongModel]:
    filters = []
    if not show_blocked_songs:
        filters.append(models.SongModel.blocked == False)
    songs = user.favorite_songs.filter(and_(True, *filters)).all()
    return songs


def update_user_sub(
    pdb: Session, user: models.UserModel, user_update_sub: schemas.UserUpdateSub
) -> models.UserModel:
    user_update_sub = user_update_sub.dict(exclude_none=False)

    for key, value in user_update_sub.items():
        setattr(user, key, value)

    pdb.commit()
    pdb.refresh(user)
    print(user.sub_expires)
    return user
