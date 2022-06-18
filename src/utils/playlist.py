import json

from src.database.access import get_db
from src.database import models
from src import roles, utils
from src import schemas
from typing import Optional, List
from fastapi import HTTPException, Depends, Form
from sqlalchemy.orm import Session

from src.roles import get_role


def get_colab_from_form(pdb: Session = Depends(get_db), colab_id: str = Form(...)):
    return models.UserModel.get(pdb, _id=colab_id)


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


def retrieve_playlist(
    resource: schemas.ResourceBase = Depends(utils.resource.retrieve_resource),
    songs_ids: List[int] = Depends(utils.song.retrieve_songs_ids),
    colabs_ids: List[str] = Depends(retrieve_colabs_ids),
):
    return schemas.PlaylistPost(
        songs_ids=songs_ids, colabs_ids=colabs_ids, **resource.dict()
    )


def get_playlist(
    playlist_id: int, pdb=Depends(get_db), role: roles.Role = Depends(get_role)
):
    return models.PlaylistModel.get(pdb, _id=playlist_id, role=role)


def can_edit_playlist(playlist: models.PlaylistModel, role: roles.Role, uid: str):
    return (
        uid == playlist.creator_id
        or uid in [colab.id for colab in playlist.colabs]
        or role.can_edit_everything()
    )


def retrieve_playlist_update(
    resource_update: schemas.ResourceUpdate = Depends(
        utils.resource.retrieve_resource_update
    ),
    songs_ids: Optional[List[int]] = Depends(utils.song.retrieve_songs_ids_update),
    colabs_ids: Optional[List[str]] = Depends(retrieve_colabs_ids),
):

    return schemas.PlaylistUpdate(
        songs_ids=songs_ids, colabs_ids=colabs_ids, **resource_update.dict()
    )
