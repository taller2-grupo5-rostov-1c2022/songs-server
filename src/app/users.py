from src.postgres import schemas
from typing import List
from fastapi import APIRouter
from fastapi import Depends, HTTPException, Form, Header, UploadFile
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.firebase.access import get_bucket
from src.postgres.models import UserModel

router = APIRouter(tags=["users"])


@router.get("/users/", response_model=List[schemas.UserBase])
def get_all_users(pdb: Session = Depends(get_db)):
    """Returns all users"""
    users = pdb.query(UserModel).all()
    return users


@router.get("/users/{uid}", response_model=schemas.UserBase)
def get_user_by_id(uid: str, pdb: Session = Depends(get_db)):
    """Returns an user by its id or 404 if not found"""
    user = pdb.query(UserModel).filter(UserModel.id == uid).first()
    return user


@router.get("/my_users/", response_model=schemas.UserBase)
def get_my_user(
    uid: str = Header(...),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Returns own user"""
    user = pdb.query(UserModel).filter(UserModel.id == uid).first()

    blob = bucket.blob(f"pfp/{uid}")
    if blob.exists():
        blob.make_public()
        user.pfp = blob.public_url

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
):
    """Creates an user and returns its id"""
    new_user = UserModel(
        id=uid, name=name, wallet=wallet, location=location, interests=interests
    )
    pdb.add(new_user)
    pdb.commit()
    pdb.refresh(new_user)

    if img is not None:
        try:
            blob = bucket.blob("pfp/" + uid)
            blob.upload_from_file(img.file)
            blob.make_public()
        except Exception as entry_not_found:
            raise HTTPException(
                status_code=404, detail=f"Image for User '{uid}' not found"
            ) from entry_not_found

    return new_user


@router.put("/users/{uid}", response_model=schemas.UserBase)
def put_user(
    uid: str = Header(...),
    name: str = Form(None),
    wallet: str = Form(None),
    location: str = Form(None),
    interests: str = Form(None),
    img: UploadFile = None,
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Updates an user and returns its id"""
    user = pdb.query(UserModel).filter(UserModel.id == uid).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User '{uid}' not found")

    if name is not None:
        user.name = name

    if wallet is not None:
        user.wallet = wallet

    if location is not None:
        user.location = location

    if interests is not None:
        user.interests = interests

    pdb.commit()

    if img is not None:
        try:
            blob = bucket.blob("pfp/" + uid)
            blob.upload_from_file(img.file)
            blob.make_public()
        except Exception as entry_not_found:
            raise HTTPException(
                status_code=404, detail=f"Image for User '{uid}' not found"
            ) from entry_not_found

    return user


@router.delete("/users/")
def delete_user(uid: str, pdb: Session = Depends(get_db)):
    """Deletes an user given its id or 404 if not found"""

    user = pdb.query(UserModel).filter(UserModel.id == uid).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User '{uid}' not found")
    pdb.query(UserModel).filter(UserModel.id == uid).delete()
    pdb.commit()
