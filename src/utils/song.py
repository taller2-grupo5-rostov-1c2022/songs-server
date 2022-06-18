import json
from src.database import models
from fastapi import HTTPException, Depends, Form
from src import schemas
from sqlalchemy.orm import Session
from .. import roles, utils
from typing import List, Optional

from src.database.access import get_db
from ..roles import get_role


def retrieve_songs_ids(songs_ids: Optional[str] = Form(None)):
    if songs_ids is None:
        return []
    try:
        songs_ids = json.loads(songs_ids)
        return songs_ids
    except ValueError:
        raise HTTPException(
            status_code=422, detail="Songs ids string is not well encoded"
        )


def retrieve_songs_ids_update(songs_ids: Optional[str] = Form(None)):
    if songs_ids is None:
        return []
    else:
        return retrieve_songs_ids(songs_ids=songs_ids)


def retrieve_song_update(
    resource_creator_update: schemas.ResourceCreatorUpdate = Depends(
        utils.resource.retrieve_resource_creator_update
    ),
    artists_names: Optional[List[str]] = Depends(
        utils.artist.retrieve_artists_names_update
    ),
):
    return schemas.SongUpdate(
        artists_names=artists_names, **resource_creator_update.dict()
    )


def get_song(
    song_id: int,
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
    user: models.UserModel = Depends(utils.user.retrieve_user),
):
    song = models.SongModel.get(pdb, role=role, _id=song_id)

    if song.sub_level > user.sub_level and not role.ignore_sub_level():
        raise HTTPException(
            status_code=403,
            detail=f"You are not allowed to see this song, expected at least level {song.sub_level}, you have level {user.sub_level}",
        )
    return song


def get_song_from_form(
    song_id: int = Form(...),
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
    user: models.UserModel = Depends(utils.user.retrieve_user),
):
    return get_song(song_id=song_id, role=role, pdb=pdb, user=user)


def retrieve_song(
    resource_creator: schemas.ResourceCreatorBase = Depends(
        utils.resource.retrieve_resource_creator
    ),
    artists_names: List[str] = Depends(utils.artist.retrieve_artists_names),
    album_id: Optional[str] = Form(None),
    sub_level: Optional[int] = Form(None),
):
    if sub_level is None:
        sub_level = 0
    song = schemas.SongPost(
        artists_names=artists_names,
        album_id=album_id,
        sub_level=sub_level,
        **resource_creator.dict(),
    )
    return song
