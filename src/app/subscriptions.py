from src.exceptions import MessageException
import datetime

from fastapi import APIRouter, Depends, Body
from typing import List

from src import utils, schemas, roles
from src.roles import get_role
from src.utils.subscription import SUBSCRIPTIONS, SUB_LEVEL_FREE, SUB_LEVEL_GOD
from sqlalchemy.orm import Session
from src.database import models
from src.database.access import get_db

router = APIRouter(tags=["subscriptions"])


def get_time_now() -> datetime.datetime:
    return datetime.datetime.now()


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


@router.post("/subscriptions/revoke/")
def refresh_subscription(
    pdb: Session = Depends(get_db),
    now: datetime.datetime = Depends(get_time_now),
    role: roles.Role = Depends(get_role),
):
    """Refreshes subscription"""
    if not role.can_revoke():
        raise MessageException(
            status_code=403, detail="You are not allowed to revoke subscriptions"
        )
    utils.subscription.revoke_subscription(pdb, now)
