from src import roles, utils, schemas
from src.database.access import get_db
from typing import Optional
from fastapi import APIRouter
from fastapi import Depends, HTTPException, UploadFile, Query
from sqlalchemy.orm import Session
from src.firebase.access import get_bucket, get_auth
from src.database import models

from src.schemas.pagination import CustomPage

router = APIRouter(tags=["users"])


@router.get("/users/", response_model=CustomPage[schemas.UserGet])
def get_all_users(
    pdb: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: Optional[str] = Query(None),
):
    """Returns all users"""

    users = models.UserModel.search(pdb, limit=limit, offset=offset)

    return users


@router.get("/users/{uid}", response_model=schemas.UserGetById)
def get_user_by_id(uid: str, pdb: Session = Depends(get_db)):
    """Returns a user by its id or 404 if not found"""

    user = models.UserModel.get(pdb, _id=uid)

    return user


@router.get("/my_user/", response_model=schemas.UserGetById)
def get_my_user(user: models.UserModel = Depends(utils.user.retrieve_user)):
    """Returns own user"""

    return user


@router.post("/users/", response_model=schemas.UserGetById)
def post_user(
    user_info: schemas.UserCreate = Depends(utils.user.retrieve_user_info),
    img: UploadFile = None,
    bucket=Depends(get_bucket),
    auth=Depends(get_auth),
    pdb: Session = Depends(get_db),
):
    """Creates a user and returns its id"""

    wallet = utils.subscription.create_wallet(user_info.uid)

    user_info = user_info.dict()
    user_info["id"] = user_info["uid"]

    if img:
        user = models.UserModel.create(
            pdb, **user_info, wallet=wallet, pfp=img.file, bucket=bucket
        )
        auth.update_user(uid=user_info["id"], photo_url=user.pfp_url)
    else:
        user = models.UserModel.create(pdb, **user_info, wallet=wallet)

    auth.update_user(uid=user.id, display_name=user.name)
    return user


@router.put("/users/{uid_to_modify}", response_model=schemas.UserGetById)
def put_user(
    uid: str = Depends(utils.user.retrieve_uid),
    user_to_modify: models.UserModel = Depends(utils.user.retrieve_user_to_modify),
    user_update: schemas.UserUpdate = Depends(utils.user.retrieve_user_update),
    pdb: Session = Depends(get_db),
    img: Optional[UploadFile] = None,
    bucket=Depends(get_bucket),
    auth=Depends(get_auth),
):
    """Updates a user and returns its id or 404 if not found or 403 if not authorized to update"""
    if uid != user_to_modify.id:
        raise HTTPException(
            status_code=403,
            detail=f"User with id {uid} attempted to modify user of id {user_to_modify.id}",
        )

    if img:
        modified_user = user_to_modify.update(
            pdb, **user_update.dict(exclude_none=True), pfp=img.file, bucket=bucket
        )
        auth.update_user(uid=uid, photo_url=modified_user.pfp_url)
    else:
        modified_user = user_to_modify.update(
            pdb, **user_update.dict(exclude_none=True)
        )
    if user_update.name is not None:
        auth.update_user(uid=uid, display_name=user_update.name)

    return modified_user


@router.delete("/users/{uid_to_delete}")
def delete_user(
    uid_to_delete: str,
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Deletes a user given its id or 404 if not found or 403 if not authorized to delete"""

    if user.id != uid_to_delete:
        raise HTTPException(
            status_code=403,
            detail=f"User with id {user.id} attempted to delete user of id {uid_to_delete}",
        )

    utils.user.give_ownership_of_playlists_to_colabs(user)

    user.delete(pdb, bucket=bucket)


@router.post("/users/make_artist/")
def make_artist(
    uid: str = Depends(utils.user.retrieve_uid),
    role: roles.Role = Depends(roles.get_role),
    auth=Depends(get_auth),
):
    if role != roles.Role.listener():
        raise HTTPException(status_code=405, detail="Not a listener")

    auth.set_custom_user_claims(uid, {"role": str(roles.Role.artist())})
