from fastapi import APIRouter, Depends, Body
from typing import List

from src import utils, schemas
from src.utils.subscription import SUBSCRIPTIONS, SUB_LEVEL_FREE, SUB_LEVEL_GOD
from sqlalchemy.orm import Session
from src.database import models
from src.database.access import get_db

router = APIRouter(tags=["subscriptions"])


@router.get("/subscriptions/", response_model=List[schemas.SubscriptionBase])
def get_subscriptions():
    """Returns subscription prices"""

    return SUBSCRIPTIONS


@router.post("/subscriptions/")
def subscribe(
    user: models.UserModel = Depends(utils.user.retrieve_user),
    sub_level: int = Body(..., ge=SUB_LEVEL_FREE, le=SUB_LEVEL_GOD, embed=True),
    pdb: Session = Depends(get_db),
):
    """Subscribes user to a subscription level"""

    utils.subscription.subscribe(user, sub_level, pdb)
