from src.postgres import schemas
from typing import List
from fastapi import APIRouter
from fastapi import Depends, HTTPException

from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres.models import UserModel

router = APIRouter(tags=["users"])


@router.get("/users/", response_model=List[schemas.UserBase])
def get_all_users(pdb: Session = Depends(get_db)):
    """Returns all users"""
    users = pdb.query(UserModel).all()
    return users


@router.get("/users/{user_id}", response_model=schemas.UserBase)
def get_user_by_id(user_id: str, pdb: Session = Depends(get_db)):
    """Returns a user by its id or 404 if not found"""
    user = pdb.query(UserModel).filter_by(UserModel.id == user_id).first()
    return user


@router.post("/users/")
def post_user(user_id: str, user_name: str, pdb: Session = Depends(get_db)):
    """Creates a user and returns its id"""
    new_user = UserModel(id=user_id, name=user_name)
    pdb.add(new_user)
    pdb.commit()
    pdb.refresh(new_user)

    return {"user_id": user_id}


@router.delete("/users/")
def delete_user(user_id: str, pdb: Session = Depends(get_db)):
    """Deletes a user given its id or 404 if not found"""

    user = pdb.query(UserModel).filter_by(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    pdb.query(UserModel).filter_by(UserModel.id == user_id).delete()
    pdb.commit()
