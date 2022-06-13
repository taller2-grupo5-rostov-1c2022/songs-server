from fastapi import APIRouter, Depends, Body
from typing import List
from src.repositories.subscription_utils import SUBSCRIPTIONS
from src.repositories import subscription_utils
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres import models, schemas
from src.repositories import user_utils

router = APIRouter(tags=["subscriptions"])


@router.get("/subscriptions/", response_model=List[schemas.SubscriptionBase])
def get_subscriptions():
    """Returns subscription prices"""

    return SUBSCRIPTIONS


@router.post("/subscriptions/")
def subscribe(
    user: models.UserModel = Depends(user_utils.retrieve_user),
    sub_level: schemas.SubLevelBase = Depends(subscription_utils.get_valid_sub_level),
    pdb: Session = Depends(get_db),
):
    """Subscribes user to a subscription level"""

    subscription_utils.subscribe(user, sub_level.sub_level, pdb)
