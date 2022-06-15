import datetime
from fastapi import HTTPException, Header, Depends

from src import roles
from src.constants import STORAGE_PATH
from src.postgres import models
from src.postgres.database import get_db
from sqlalchemy import and_
from sqlalchemy.orm import contains_eager

from src.postgres.models import (
    song_playlist_association_table,
    playlist_favorite_association_table,
)


def retrieve_uid(uid: str = Header(...), pdb=Depends(get_db)):
    # The user is not in the database
    if pdb.get(models.UserModel, uid) is None:
        raise HTTPException(status_code=404, detail=f"User with ID {uid} not found")
    return uid


def get_favorite_songs(pdb, uid: str, role: roles.Role):
    user = get_user(uid, pdb)
    if role.can_see_blocked():
        return user.favorite_songs.all()
    else:
        return user.favorite_songs.filter(models.SongModel.blocked == False).all()


def get_user(uid: str, pdb=Depends(get_db)):
    user = pdb.get(models.UserModel, uid)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with ID {uid} not found")
    return user


def retrieve_user(uid: str = Header(...), pdb=Depends(get_db)):
    return get_user(uid, pdb)


def add_song_to_favorites(pdb, user: models.UserModel, song: models.SongModel):
    user.favorite_songs.append(song)

    pdb.commit()
    return song


def remove_song_from_favorites(pdb, user: models.UserModel, song: models.SongModel):
    if song in user.favorite_songs:
        user.favorite_songs.remove(song)
        pdb.commit()
    else:
        raise HTTPException(
            status_code=404, detail=f"Song {song.id} not found in favorites"
        )


def get_favorite_albums(pdb, uid: str, role: roles.Role):
    user = get_user(uid, pdb)
    join_conditions = [models.SongModel.album_id == models.AlbumModel.id]
    filters = []
    if not role.can_see_blocked():
        filters.append(models.AlbumModel.blocked == False)
        join_conditions.append(models.SongModel.blocked == False)

    albums = (
        user.favorite_albums.options(contains_eager("songs"))
        .join(models.SongModel, and_(*join_conditions), full=True)
        .filter(*filters)
        .all()
    )
    return albums


def add_album_to_favorites(pdb, user: models.UserModel, album: models.AlbumModel):
    user.favorite_albums.append(album)
    pdb.commit()
    return album


def remove_album_from_favorites(pdb, user: models.UserModel, album: models.AlbumModel):
    if album in user.favorite_albums:
        user.favorite_albums.remove(album)
        pdb.commit()
    else:
        raise HTTPException(
            status_code=404, detail=f"Album {album.id} not found in favorites"
        )


def get_favorite_playlists(pdb, uid: str, role: roles.Role):
    filters = [models.UserModel.id == uid]
    join_conditions = []
    if not role.can_see_blocked():
        filters.append(models.PlaylistModel.blocked == False)
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
        .filter(and_(True, *filters))
    ).all()

    playlists = [p for p in playlists if p is not None]

    return playlists


def add_playlist_to_favorites(
    pdb, user: models.UserModel, playlist: models.PlaylistModel
):
    user.favorite_playlists.append(playlist)
    pdb.commit()
    return playlist


def remove_playlist_from_favorites(
    pdb, user: models.UserModel, playlist: models.PlaylistModel
):
    if playlist in user.favorite_playlists:
        user.favorite_playlists.remove(playlist)
        pdb.commit()
    else:
        raise HTTPException(
            status_code=404, detail=f"Playlist {playlist.id} not found in favorites"
        )


def pfp_url(user: models.UserModel):
    if user.pfp_last_update is not None:
        return (
            STORAGE_PATH
            + "pfp/"
            + str(user.id)
            + "?t="
            + str(int(datetime.datetime.timestamp(user.pfp_last_update)))
        )


def give_ownership_of_playlists_to_colabs(user: models.UserModel):
    for playlist in user.my_playlists:
        if len(playlist.colabs) > 0:
            playlist.creator = playlist.colabs[0]
            playlist.colabs.remove(playlist.creator)
