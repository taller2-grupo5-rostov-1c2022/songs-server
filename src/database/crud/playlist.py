from typing import Optional, List

from sqlalchemy.orm import Session, contains_eager
from sqlalchemy.sql import or_, and_
from fastapi import HTTPException, status
from src import schemas, utils
from src.database import models, crud


def get_playlist_by_id(
    pdb: Session, playlist_id: int, show_blocked_songs: bool, show_blocked_albums: bool
):
    join_conditions = [
        models.SongModel.id == models.song_playlist_association_table.c.song_id
    ]
    filters = [playlist_id == models.PlaylistModel.id]
    if not show_blocked_songs:
        join_conditions.append(models.SongModel.blocked == False)
    if not show_blocked_albums:
        filters.append(models.PlaylistModel.blocked == False)

    playlists = (
        pdb.query(models.PlaylistModel)
        .join(
            models.song_playlist_association_table,
            models.song_playlist_association_table.c.playlist_id
            == models.PlaylistModel.id,
            isouter=True,
        )
        .join(models.SongModel, and_(True, *join_conditions), isouter=True)
        .options(contains_eager("songs"))
        .filter(and_(True, *filters))
    ).all()

    if len(playlists) == 0:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlists[0]


def get_playlists(
    pdb: Session,
    show_blocked_songs: bool,
    show_blocked_playlists,
    colab_id: Optional[str],
) -> List[models.PlaylistModel]:
    queries = []
    join_conditions = []
    if not show_blocked_songs:
        join_conditions.append(models.SongModel.blocked == False)
    if not show_blocked_playlists:
        queries.append(models.PlaylistModel.blocked == False)

    if colab_id is not None:
        queries.append(
            or_(
                models.PlaylistModel.creator_id == colab_id,
                models.UserModel.id == colab_id,
            )
        )

    playlists = (
        pdb.query(models.PlaylistModel)
        .join(models.UserModel.other_playlists, full=True)
        .join(models.SongModel, and_(True, *join_conditions), full=True)
        .filter(*queries)
        .all()
    )

    playlists = [p for p in playlists if p is not None]

    return playlists


def create_playlist(
    pdb: Session, playlist_info: schemas.PlaylistPost, can_see_blocked: bool
) -> models.PlaylistModel:
    songs = crud.song.get_songs_by_id(pdb, playlist_info.songs_ids, can_see_blocked)
    colabs = utils.playlist.get_colabs_list(pdb, playlist_info.colabs_ids)

    playlist = models.PlaylistModel(
        **playlist_info.dict(exclude={"songs_ids", "colabs_ids"}),
        colabs=colabs,
        songs=songs,
    )
    pdb.add(playlist)
    pdb.commit()

    return playlist


def update_playlist(
    pdb: Session,
    playlist: models.PlaylistModel,
    playlist_update: schemas.PlaylistUpdate,
    show_blocked_songs: bool,
    can_block: bool,
):
    songs_ids = playlist_update.songs_ids
    colabs_ids = playlist_update.colabs_ids
    blocked = playlist_update.blocked
    playlist_update = playlist_update.dict(
        exclude_none=True, exclude={"songs_ids", "colabs_ids", "blocked"}
    )

    for playlist_attr in playlist_update:
        setattr(playlist, playlist_attr, playlist_update[playlist_attr])

    if colabs_ids is not None:
        colabs = utils.playlist.get_colabs_list(pdb, colabs_ids)
        playlist.colabs = colabs

    if songs_ids is not None:
        songs = crud.song.get_songs_by_id(pdb, songs_ids, show_blocked_songs)
        playlist.songs = songs

    if blocked is not None:
        if not can_block:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't block playlists",
            )
        playlist.blocked = blocked

    pdb.commit()


def delete_playlist(pdb: Session, playlist: models.PlaylistModel):
    pdb.delete(playlist)
    pdb.commit()


def add_song(pdb: Session, playlist: models.PlaylistModel, song: models.SongModel):
    if song not in playlist.songs:
        playlist.songs.append(song)
        pdb.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Song is already in playlist"
        )


def remove_song(pdb: Session, playlist: models.PlaylistModel, song: models.SongModel):
    if song in playlist.songs:
        playlist.songs.remove(song)
        pdb.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Song is not in playlist"
        )


def add_colab(pdb: Session, playlist: models.PlaylistModel, colab: models.UserModel):
    if colab not in playlist.colabs:
        playlist.colabs.append(colab)
        pdb.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Colab is already in playlist"
        )
