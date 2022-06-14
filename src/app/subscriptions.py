from fastapi import APIRouter, Depends
from typing import List

from src import utils
from src.utils.subscription import SUBSCRIPTIONS
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.database import models
from src.postgres import schemas

router = APIRouter(tags=["subscriptions"])


@router.get("/subscriptions/", response_model=List[schemas.SubscriptionBase])
def get_subscriptions():
    """Returns subscription prices"""

    return SUBSCRIPTIONS


@router.post("/subscriptions/")
def subscribe(
    user: models.UserModel = Depends(utils.user.retrieve_user),
    sub_level: int = Depends(utils.subscription.get_valid_sub_level),
    pdb: Session = Depends(get_db),
):
    """Subscribes user to a subscription level"""

    utils.subscription.subscribe(user, sub_level, pdb)
