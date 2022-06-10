import datetime
from sqlalchemy.orm import Session
from fastapi import status, HTTPException
import requests

from src.postgres import schemas

DEPOSIT_ENDPOINT = "https://rostov-payments-server.herokuapp.com/api/v1/deposit"
CREATE_WALLET_ENDPOINT = "https://rostov-payments-server.herokuapp.com/api/v1/wallets"


SUB_LEVEL_FREE = 0

SUB_LEVEL_PREMIUM = 1

SUB_LEVEL_PRO = 2

SUBSCRIPTIONS = [
    {"name": "Free", "price": "0", "level": SUB_LEVEL_FREE},
    {"name": "Premium", "price": "0.0000001", "level": SUB_LEVEL_PREMIUM},
    {"name": "Pro", "price": "0.0000005", "level": SUB_LEVEL_PRO},
]

SUB_LEVELS_DAYS_TO_EXPIRE = {
    SUB_LEVEL_FREE: None,
    SUB_LEVEL_PREMIUM: 30,
    SUB_LEVEL_PRO: 30,
}


def get_subscriptions():
    """Returns subscription prices"""

    return SUBSCRIPTIONS


def create_wallet(uid: str):
    response = requests.post(f"{CREATE_WALLET_ENDPOINT}/:{uid}")

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text,
        )
    return response.json()["address"]


def get_days_to_expire(sub_level: int):
    return SUB_LEVELS_DAYS_TO_EXPIRE[sub_level]


def get_valid_sub_level(sub_level: schemas.SubLevelBase):
    """Returns a valid subscription level"""

    if sub_level.sub_level not in [0, 1, 2]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription level",
        )
    return sub_level


def get_sub_price(sub_level: int):
    """Returns the price of a subscription level"""

    for subscription in SUBSCRIPTIONS:
        if subscription["level"] == sub_level:
            return subscription["price"]

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid subscription level",
    )


def subscribe(user: schemas.UserBase, sub_level: int, pdb: Session):
    if sub_level == 0:
        user.sub_level = 0
        user.sub_expires = None
    else:
        payment_response = requests.post(
            f"{DEPOSIT_ENDPOINT}/:{user.id}",
            json={"amountInEthers": get_sub_price(sub_level)},
        )

        if payment_response.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=payment_response.status_code,
                detail=payment_response.text,
            )

        user.sub_level = sub_level
        expiration_date = datetime.datetime.now() + datetime.timedelta(
            days=get_days_to_expire(sub_level)
        )
        expiration_date = expiration_date.replace(minute=0, second=0, microsecond=0)

        user.sub_expires = expiration_date

    pdb.commit()
    pdb.refresh(user)
