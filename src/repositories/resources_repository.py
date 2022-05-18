from fastapi import Form, Depends, HTTPException, Header
from typing import Optional, List
import json
from src.postgres import schemas
from src.postgres.database import get_db
from src.postgres.models import AlbumModel, UserModel, ArtistModel
from src.postgres.schemas import AlbumInfoBase, ArtistBase


def retrieve_uid(uid: str = Header(...), pdb = Depends(get_db)):
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
    name: str = Form(...), description: str = Form(...), uid: str = Header(...)
):
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
        return None
    try:
        songs_ids = json.loads(songs_ids)
        return songs_ids
    except ValueError:
        HTTPException(status_code=422, detail=f"Songs ids string is not well encoded")


def retrieve_album_update(
    resource_creator_update: schemas.ResourceCreatorUpdate = Depends(
        retrieve_resource_creator_update
    ),
    songs_ids: Optional[List[int]] = Depends(retrieve_songs_ids),
):
    return schemas.AlbumUpdate(songs_ids=songs_ids, **resource_creator_update.dict())


def retrieve_album(
    resource_creator: schemas.ResourceCreator = Depends(retrieve_resource_creator),
    songs_ids: List[int] = Depends(retrieve_songs_ids),
):
    return schemas.AlbumPost(songs_ids=songs_ids, **resource_creator.dict())


def retrieve_artists_names_update(
        artists: Optional[str] = Form(None)
):
    if artists is not None:
        try:
            artists = json.loads(artists)
            if len(artists) == 0:
                raise HTTPException(status_code=422, detail="There must be at least one artist")
        except ValueError as e:
            raise HTTPException(
                status_code=422, detail="Artists string is not well encoded"
            ) from e
    return artists


def retrieve_artists_names(
    artists: str = Form(...),
):
    return retrieve_artists_names_update(artists=artists)


def retrieve_album_info(
        album: Optional[int] = Form(None),
        pdb=Depends(get_db)
):

    if album is not None:
        album_id = album
        album = pdb.get(AlbumModel, album_id)
        if album is None:
            raise HTTPException(
                status_code=404, detail="Album not found"
            )
    return album


def retrieve_song(
        resource_creator: schemas.ResourceCreator = Depends(retrieve_resource_creator),
        artists_names: List[str] = Depends(retrieve_artists_names),
        album_info: Optional[AlbumInfoBase] = Depends(retrieve_album_info)
):
    return schemas.SongPost(artists_names=artists_names, album=album_info, **resource_creator.dict())


def retrieve_song_update(
        resource_creator_update: schemas.ResourceCreatorUpdate = Depends(retrieve_resource_creator_update),
        artists_names: Optional[List[str]] = Depends(retrieve_artists_names_update),
):
    return schemas.SongUpdate(artists_names=artists_names, **resource_creator_update.dict())