from src import roles
from src.constants import STORAGE_PATH, SUPPRESS_BLOB_ERRORS
from src.postgres import schemas
from typing import List
from fastapi import APIRouter
from fastapi import Depends, HTTPException, Form, Header, UploadFile
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.firebase.access import get_bucket, get_auth
from src.postgres import models
import datetime

from src.repositories import (
    user_utils,
    comment_utils,
    song_utils,
    album_utils,
    playlist_utils,
)

router = APIRouter(tags=["users"])


@router.get("/users/", response_model=List[schemas.UserBase])
def get_all_users(pdb: Session = Depends(get_db)):
    """Returns all users"""
    users = pdb.query(models.UserModel).all()
    return users


@router.get("/users/{uid}", response_model=schemas.UserBase)
def get_user_by_id(
    uid: str,
    pdb: Session = Depends(get_db),
):
    """Returns an user by its id or 404 if not found"""
    user = pdb.get(models.UserModel, uid)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.pfp = STORAGE_PATH + "pfp/" + str(uid) + "?t=" + str(user.pfp_last_update)

    return user


@router.get("/my_user/", response_model=schemas.UserBase)
def get_my_user(
    uid: str = Header(...),
    pdb: Session = Depends(get_db),
):
    """Returns own user"""
    user = pdb.get(models.UserModel, uid)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

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
    new_user = models.UserModel(
        id=uid,
        name=name,
        wallet=wallet,
        location=location,
        interests=interests,
        pfp_last_update=datetime.datetime.now(),
    )

    auth.update_user(uid=uid, display_name=name)

    if img is not None:
        try:
            blob = bucket.blob("pfp/" + uid)
            blob.upload_from_file(img.file)
            blob.make_public()
            auth.update_user(uid=uid, photo_url=blob.public_url)
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

    user = (
        pdb.query(models.UserModel).filter(models.UserModel.id == uid_to_modify).first()
    )

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

    user = pdb.query(models.UserModel).filter(models.UserModel.id == uid).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User '{uid}' not found")
    pdb.delete(user)

    try:
        bucket.blob("pfp/" + str(uid)).delete()
    except:  # noqa: W0707 # Want to catch all exceptions
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507, detail=f"Image for User '{uid}' could not be deleted"
            )

    pdb.commit()


@router.get("/users/{uid}/comments/", response_model=List[schemas.CommentMyComments])
def get_comments_of_user(
    uid: str = Depends(user_utils.retrieve_uid), pdb: Session = Depends(get_db)
):
    return comment_utils.get_comments_by_uid(pdb, uid)


@router.get("/users/{uid}/favorites/songs/", response_model=List[schemas.SongBase])
def get_favorite_songs(
    uid: str = Depends(user_utils.retrieve_uid),
    role: roles.Role = Depends(roles.get_role),
    pdb: Session = Depends(get_db),
):
    return user_utils.get_favorite_songs(pdb, uid, role)


@router.post("/users/{uid}/favorites/songs/", response_model=schemas.SongBase)
def add_song_to_favorites(
    song: models.SongModel = Depends(song_utils.get_song),
    user: models.UserModel = Depends(user_utils.get_user),
    pdb: Session = Depends(get_db),
):
    return user_utils.add_song_to_favorites(pdb, user, song)


@router.delete("/users/{uid}/favorites/songs/")
def remove_song_from_favorites(
    song: models.SongModel = Depends(song_utils.get_song),
    user: models.UserModel = Depends(user_utils.get_user),
    pdb: Session = Depends(get_db),
):
    return user_utils.remove_song_from_favorites(pdb, user, song)


@router.get("/users/{uid}/favorites/albums/", response_model=List[schemas.AlbumBase])
def get_favorite_albums(
    uid: str = Depends(user_utils.retrieve_uid),
    role: roles.Role = Depends(roles.get_role),
    pdb: Session = Depends(get_db),
):
    return user_utils.get_favorite_albums(pdb, uid, role)


@router.post("/users/{uid}/favorites/albums/", response_model=schemas.AlbumBase)
def add_album_to_favorites(
    album: models.AlbumModel = Depends(album_utils.get_album),
    user: models.UserModel = Depends(user_utils.get_user),
    pdb: Session = Depends(get_db),
):
    return user_utils.add_album_to_favorites(pdb, user, album)


@router.delete("/users/{uid}/favorites/albums/")
def remove_album_from_favorites(
    album: models.AlbumModel = Depends(album_utils.get_album),
    user: models.UserModel = Depends(user_utils.get_user),
    pdb: Session = Depends(get_db),
):
    return user_utils.remove_album_from_favorites(pdb, user, album)


@router.get(
    "/users/{uid}/favorites/playlists/", response_model=List[schemas.PlaylistBase]
)
def get_favorite_playlists(
    uid: str = Depends(user_utils.retrieve_uid),
    role: roles.Role = Depends(roles.get_role),
    pdb: Session = Depends(get_db),
):
    return user_utils.get_favorite_playlists(pdb, uid, role)


@router.post("/users/{uid}/favorites/playlists/", response_model=schemas.PlaylistBase)
def add_playlist_to_favorites(
    playlist: models.PlaylistModel = Depends(playlist_utils.get_playlist),
    user: models.UserModel = Depends(user_utils.get_user),
    pdb: Session = Depends(get_db),
):
    return user_utils.add_playlist_to_favorites(pdb, user, playlist)
