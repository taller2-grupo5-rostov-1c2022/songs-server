from src import roles, utils, schemas
from src.constants import SUPPRESS_BLOB_ERRORS
from src.database.access import get_db
from typing import List
from fastapi import APIRouter
from fastapi import Depends, HTTPException, Form, Header, UploadFile
from sqlalchemy.orm import Session
from src.firebase.access import get_bucket, get_auth
from src.database import models, crud
import datetime
from src.utils.subscription import SUB_LEVEL_FREE

router = APIRouter(tags=["users"])


@router.get("/users/", response_model=List[schemas.User])
def get_all_users(pdb: Session = Depends(get_db)):
    """Returns all users"""

    users = crud.user.get_users(pdb)

    for user in users:
        user.pfp = utils.user.pfp_url(user)

    return users


@router.get("/users/{uid}", response_model=schemas.User)
def get_user_by_id(uid: str, pdb: Session = Depends(get_db)):
    """Returns a user by its id or 404 if not found"""

    user = crud.user.get_user_by_id(pdb, uid)

    user.pfp = utils.user.pfp_url(user)

    return user


@router.get("/my_user/", response_model=schemas.User)
def get_my_user(user: models.UserModel = Depends(utils.user.retrieve_user)):
    """Returns own user"""

    user.pfp = utils.user.pfp_url(user)

    return user


@router.post("/users/", response_model=schemas.User)
def post_user(
    user_info: schemas.UserPost = Depends(utils.user.retrieve_user_info),
    img: UploadFile = None,
    bucket=Depends(get_bucket),
    auth=Depends(get_auth),
    pdb: Session = Depends(get_db),
):
    """Creates a user and returns its id"""

    wallet = utils.subscription.create_wallet(user_info.uid)

    user_info = user_info.dict()
    user_info["id"] = user_info["uid"]

    user_info_complete = schemas.UserPostComplete(
        **user_info,
        sub_level=SUB_LEVEL_FREE,
        wallet=wallet,
        sub_expires=utils.subscription.get_expiration_date(
            utils.subscription.SUB_LEVEL_FREE, datetime.datetime.now()
        ),
        songs=[],
        albums=[],
        playlists=[],
        my_playlists=[],
        other_playlists=[],
    )

    user = crud.user.create_user(pdb, user_info_complete)

    auth.update_user(uid=user_info_complete.uid, display_name=user_info_complete.name)

    if img is not None:
        try:
            blob = bucket.blob("pfp/" + user_info_complete.uid)
            blob.upload_from_file(img.file)
            blob.make_public()
            auth.update_user(uid=user_info_complete.uid, photo_url=blob.public_url)
            user.pfp_last_update = datetime.datetime.now()
            pdb.commit()
        except Exception as e:
            crud.user.delete_user(pdb, user)

            if not SUPPRESS_BLOB_ERRORS:
                raise HTTPException(
                    status_code=507,
                    detail=f"Image for User '{user_info_complete.uid}' could not be uploaded",
                ) from e

    return user


@router.put("/users/{uid_to_modify}", response_model=schemas.User)
def put_user(
    uid_to_modify: str,
    uid: str = Header(...),
    name: str = Form(None),
    location: str = Form(None),
    interests: str = Form(None),
    img: UploadFile = None,
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
    auth=Depends(get_auth),
):
    """Updates a user and returns its id or 404 if not found or 403 if not authorized to update"""
    if uid != uid_to_modify:
        raise HTTPException(
            status_code=403,
            detail=f"User with id {uid} attempted to modify user of id {uid_to_modify}",
        )

    user = (
        pdb.query(models.UserModel).filter(models.UserModel.id == uid_to_modify).first()
    )

    if user is None:
        raise HTTPException(status_code=404, detail=f"User '{uid}' not found")

    if name is not None:
        user.name = name
        auth.update_user(uid=uid, display_name=name)

    if location is not None:
        user.location = location

    if interests is not None:
        user.interests = interests

    if img is not None:
        try:
            blob = bucket.blob(f"pfp/{uid}")
            blob.upload_from_file(img.file)
            blob.make_public()
            user.pfp_last_update = datetime.datetime.now()
        except Exception:  # noqa: E722 # Want to catch all exceptions
            if not SUPPRESS_BLOB_ERRORS:
                raise HTTPException(
                    status_code=507,
                    detail=f"Image for User '{uid}' could not be uploaded",
                )

    pdb.commit()

    return user


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

    pdb.delete(user)

    if user.pfp_last_update is not None:
        try:
            bucket.blob("pfp/" + str(user.id)).delete()
        except:  # noqa: W0707 # Want to catch all exceptions
            if not SUPPRESS_BLOB_ERRORS:
                raise HTTPException(
                    status_code=507,
                    detail=f"Image for User '{user.id}' could not be deleted",
                )

    pdb.commit()


@router.post("/users/make_artist/")
def make_artist(
    uid: str = Depends(utils.user.retrieve_uid),
    role: roles.Role = Depends(roles.get_role),
    auth=Depends(get_auth),
):
    if role != roles.Role.listener():
        raise HTTPException(status_code=405, detail="Not a listener")

    auth.set_custom_user_claims(uid, {"role": str(roles.Role.artist())})
