from fastapi import Header, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from src import schemas
from src.database import models
from src.database.access import get_db


def retrieve_user(uid: str = Header(...), pdb=Depends(get_db)):
    return models.UserModel.get(pdb, _id=uid)


def retrieve_uid(uid: str = Header(...), pdb=Depends(get_db)):
    return retrieve_user(uid=uid, pdb=pdb).id


def retrieve_user_info(
    uid: str = Header(...),
    name: str = Form(...),
    location: str = Form(...),
    interests: str = Form(...),
    pdb: Session = Depends(get_db),
) -> schemas.UserCreate:

    user = models.UserModel.get(pdb, _id=uid, raise_if_not_found=False)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    user_info = schemas.UserCreate(
        uid=uid, name=name, location=location, interests=interests
    )
    return user_info


def retrieve_user_update(
    name: str = Form(None), location: str = Form(None), interests: str = Form(None)
):
    user_update = schemas.UserUpdate(name=name, location=location, interests=interests)
    return user_update


def retrieve_user_to_modify(uid_to_modify: str, pdb: Session = Depends(get_db)):
    user_to_modify = models.UserModel.get(pdb, _id=uid_to_modify)

    return user_to_modify


def give_ownership_of_playlists_to_colabs(user: models.UserModel):
    for playlist in user.my_playlists:
        if len(playlist.colabs) > 0:
            playlist.creator = playlist.colabs[0]
            playlist.colabs.remove(playlist.creator)
