import datetime
from fastapi import Header, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from src import schemas
from src.constants import STORAGE_PATH
from src.database import models, crud
from src.database.access import get_db


def retrieve_user(uid: str = Header(...), pdb=Depends(get_db)):
    return crud.user.get_user_by_id(pdb, uid)


def retrieve_uid(uid: str = Header(...), pdb=Depends(get_db)):
    return crud.user.get_user_by_id(pdb, uid).id


def retrieve_user_info(
        uid: str = Header(...),
        name: str = Form(...),
        location: str = Form(...),
        interests: str = Form(...),
        pdb: Session = Depends(get_db),
) -> schemas.UserPost:
    try:
        crud.user.get_user_by_id(pdb, uid)
    except HTTPException:
        user = schemas.UserPost(uid=uid, name=name, location=location, interests=interests)
        return user
    else:
        raise HTTPException(status_code=400, detail="User already exists")


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
