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
            models.PlaylistModel.songs.and_(*join_conditions),
            isouter=True,
        )
        .options(contains_eager("songs"))
        .filter(and_(True, *filters))
    ).all()

    if len(playlists) == 0:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlists[0]
