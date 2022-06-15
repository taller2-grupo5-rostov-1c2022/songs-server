from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.database import models


def get_user_by_id(pdb: Session, uid: str) -> models.UserModel:
    colab = pdb.get(models.UserModel, uid)
    if colab is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {uid} not found",
        )
    return colab
