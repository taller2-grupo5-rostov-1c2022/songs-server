from src.constants import STORAGE_PATH, SUPPRESS_BLOB_ERRORS
from src.postgres import schemas
from typing import List
from fastapi import APIRouter
from fastapi import Depends, HTTPException, Form, Header, UploadFile
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.firebase.access import get_bucket, get_auth
from src.postgres.models import UserModel
import datetime

router = APIRouter(tags=["users"])


@router.get("/users/", response_model=List[schemas.UserBase])
def get_all_users(pdb: Session = Depends(get_db)):
    """Returns all users"""
    users = pdb.query(UserModel).all()
    return users


@router.get("/users/{uid}", response_model=schemas.UserBase)
def get_user_by_id(
    uid: str,
    pdb: Session = Depends(get_db),
):
    """Returns an user by its id or 404 if not found"""
    user = pdb.get(UserModel, uid)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.pfp_last_update is not None:
        user.pfp = (
            STORAGE_PATH
            + "pfp/"
            + str(uid)
            + "?t="
            + str(int(datetime.datetime.timestamp(user.pfp_last_update)))
        )

    return user


@router.get("/my_user/", response_model=schemas.UserBase)
def get_my_user(
    uid: str = Header(...),
    pdb: Session = Depends(get_db),
):
    """Returns own user"""
    user = pdb.get(UserModel, uid)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.pfp_last_update is not None:
        user.pfp = (
            STORAGE_PATH
            + "pfp/"
            + str(uid)
            + "?t="
            + str(int(datetime.datetime.timestamp(user.pfp_last_update)))
        )

    return user


@router.post("/users/", response_model=schemas.UserBase)
def post_user(
    uid: str = Header(...),
    name: str = Form(...),
    wallet: str = Form(None),
    location: str = Form(...),
    interests: str = Form(...),
    img: UploadFile = None,
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
    auth=Depends(get_auth),
):
    """Creates a user and returns its id"""
    new_user = UserModel(
        id=uid,
        name=name,
        wallet=wallet,
        location=location,
        interests=interests,
    )

    auth.update_user(uid=uid, display_name=name)

    if img is not None:
        try:
            blob = bucket.blob("pfp/" + uid)
            blob.upload_from_file(img.file)
            blob.make_public()
            auth.update_user(uid=uid, photo_url=blob.public_url)
            new_user.pfp_last_update = datetime.datetime.now()
        except Exception as e:
            if not SUPPRESS_BLOB_ERRORS:
                raise HTTPException(
                    status_code=507,
                    detail=f"Image for User '{uid}' could not be uploaded",
                ) from e

    pdb.add(new_user)
    pdb.commit()
    pdb.refresh(new_user)

    return new_user


@router.put("/users/{uid_to_modify}", response_model=schemas.UserBase)
def put_user(
    uid_to_modify: str,
    uid: str = Header(...),
    name: str = Form(None),
    wallet: str = Form(None),
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

    user = pdb.query(UserModel).filter(UserModel.id == uid_to_modify).first()

    if user is None:
        raise HTTPException(status_code=404, detail=f"User '{uid}' not found")

    if name is not None:
        user.name = name
        auth.update_user(uid=uid, display_name=name)

    if wallet is not None:
        user.wallet = wallet

    if location is not None:
        user.location = location

    if interests is not None:
        user.interests = interests

    if img is not None:
        try:
            blob = bucket.blob(f"pfp/{uid}")
            blob.upload_from_file(img.file)
            blob.make_public()
            user.pfp_last_update = datetime.datetime.now() + datetime.timedelta(
                seconds=1
            )
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
    uid: str = Header(...),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Deletes a user given its id or 404 if not found or 403 if not authorized to delete"""

    if uid != uid_to_delete:
        raise HTTPException(
            status_code=403,
            detail=f"User with id {uid} attempted to delete user of id {uid_to_delete}",
        )

    user = pdb.query(UserModel).filter(UserModel.id == uid).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User '{uid}' not found")
    pdb.delete(user)

    if user.pfp_last_update is not None:
        try:
            bucket.blob("pfp/" + str(uid)).delete()
        except:  # noqa: W0707 # Want to catch all exceptions
            if not SUPPRESS_BLOB_ERRORS:
                raise HTTPException(
                    status_code=507,
                    detail=f"Image for User '{uid}' could not be deleted",
                )

    pdb.commit()
