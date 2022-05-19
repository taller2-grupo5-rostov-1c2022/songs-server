from fastapi import Form, Depends, HTTPException, Header
from typing import Optional, List
import json

from src import roles
from src.postgres import schemas
from src.postgres.database import get_db
from src.postgres.models import AlbumModel, UserModel
from src.postgres.schemas import AlbumInfoBase
from sqlalchemy.orm import Session
from src.repositories import songs_repository as crud_songs

from src.roles import get_role


def retrieve_uid(uid: str = Header(...), pdb=Depends(get_db)):
    # The user is not in the database
    if pdb.get(UserModel, uid) is None:
        raise HTTPException(status_code=404, detail=f"User with ID {uid} not found")
    return uid


def retrieve_resource_update(
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    blocked: Optional[bool] = Form(None),
):
    return schemas.ResourceUpdate(name=name, description=description, blocked=blocked)


def retrieve_resource(
    name: str = Form(...),
    description: str = Form(...),
    uid: str = Header(...),
    pdb: Session = Depends(get_db),
):
    if pdb.get(UserModel, uid) is None:
        raise HTTPException(status_code=404, detail=f"User with id {uid} not found")

    return schemas.ResourceBase(
        name=name, description=description, blocked=False, creator_id=uid
    )


def retrieve_resource_creator_update(
    resource_update: schemas.ResourceUpdate = Depends(retrieve_resource_update),
    genre: Optional[str] = Form(None),
    sub_level: Optional[int] = Form(None),
):
    return schemas.ResourceCreatorUpdate(
        genre=genre, sub_level=sub_level, **resource_update.dict()
    )


def retrieve_resource_creator(
    resource: schemas.ResourceBase = Depends(retrieve_resource),
    genre: str = Form(...),
    sub_level: Optional[int] = Form(0),
):
    return schemas.ResourceCreator(genre=genre, sub_level=sub_level, **resource.dict())


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


def retrieve_album_update(
    resource_creator_update: schemas.ResourceCreatorUpdate = Depends(
        retrieve_resource_creator_update
    ),
    songs_ids: List[int] = Depends(retrieve_songs_ids),
):
    return schemas.AlbumUpdate(songs_ids=songs_ids, **resource_creator_update.dict())


def retrieve_album(
    resource_creator: schemas.ResourceCreator = Depends(retrieve_resource_creator),
    songs_ids: List[int] = Depends(retrieve_songs_ids),
):
    return schemas.AlbumPost(songs_ids=songs_ids, **resource_creator.dict())


def retrieve_artists_names_update(artists: Optional[str] = Form(None)):
    if artists is not None:
        try:
            artists = json.loads(artists)
            if len(artists) == 0:
                raise HTTPException(
                    status_code=422, detail="There must be at least one artist"
                )
        except ValueError as e:
            raise HTTPException(
                status_code=422, detail="Artists string is not well encoded"
            ) from e
    return artists


def retrieve_artists_names(
    artists: str = Form(...),
):
    return retrieve_artists_names_update(artists=artists)


def retrieve_album_info(album: Optional[int] = Form(None), pdb=Depends(get_db)):

    if album is not None:
        album_id = album
        album = pdb.get(AlbumModel, album_id)
        if album is None:
            raise HTTPException(status_code=404, detail="Album not found")
    return album


def retrieve_song(
    resource_creator: schemas.ResourceCreator = Depends(retrieve_resource_creator),
    artists_names: List[str] = Depends(retrieve_artists_names),
    album_info: Optional[AlbumInfoBase] = Depends(retrieve_album_info),
):
    return schemas.SongPost(
        artists_names=artists_names, album=album_info, **resource_creator.dict()
    )


def retrieve_song_update(
    resource_creator_update: schemas.ResourceCreatorUpdate = Depends(
        retrieve_resource_creator_update
    ),
    artists_names: Optional[List[str]] = Depends(retrieve_artists_names_update),
):
    return schemas.SongUpdate(
        artists_names=artists_names, **resource_creator_update.dict()
    )


def retrieve_colabs_ids(colabs_ids: Optional[str] = Form(None)):
    if colabs_ids is None:
        return []
    else:
        try:
            colabs_ids = json.loads(colabs_ids)
        except ValueError as e:
            raise HTTPException(
                status_code=422, detail="Colabs string is not well encoded"
            ) from e
    return colabs_ids


def retrieve_colabs_ids_update(colabs_ids: Optional[str] = Form(None)):
    if colabs_ids is None:
        return None
    else:
        return retrieve_colabs_ids(colabs_ids=colabs_ids)


def retrieve_playlist(
    resource: schemas.ResourceBase = Depends(retrieve_resource),
    songs_ids: List[int] = Depends(retrieve_songs_ids),
    colabs_ids: List[str] = Depends(retrieve_colabs_ids),
):
    return schemas.PlaylistPost(
        songs_ids=songs_ids, colabs_ids=colabs_ids, **resource.dict()
    )


def retrieve_playlist_update(
    resource_update: schemas.ResourceUpdate = Depends(retrieve_resource_update),
    songs_ids: Optional[List[int]] = Depends(retrieve_songs_ids_update),
    colabs_ids: Optional[List[str]] = Depends(retrieve_colabs_ids),
):
    return schemas.PlaylistUpdate(
        songs_ids=songs_ids, colabs_ids=colabs_ids, **resource_update.dict()
    )


def get_song(
        song_id: int,
        role: roles.Role = Depends(get_role),
        pdb: Session = Depends(get_db),

):
    return crud_songs.get_song_by_id(pdb, role, song_id)