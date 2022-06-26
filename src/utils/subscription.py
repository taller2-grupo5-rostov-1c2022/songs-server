from src.exceptions import MessageException
import datetime
from sqlalchemy.orm import Session
from fastapi import status
import requests

from src.constants import PAYMENTS_API_KEY
from src.database import models

DEPOSIT_ENDPOINT = "https://rostov-payments-server.herokuapp.com/api/v1/deposit"
CREATE_WALLET_ENDPOINT = "https://rostov-payments-server.herokuapp.com/api/v1/wallets"


SUB_LEVEL_FREE = 0
SUB_LEVEL_PREMIUM = 1
SUB_LEVEL_PRO = 2
SUB_LEVEL_GOD = 3

SUBSCRIPTIONS = [
    {"name": "Free", "price": "0", "level": SUB_LEVEL_FREE},
    {"name": "Premium", "price": "0.0000001", "level": SUB_LEVEL_PREMIUM},
    {"name": "Pro", "price": "0.0000005", "level": SUB_LEVEL_PRO},
    {"name": "God", "price": "1000", "level": SUB_LEVEL_GOD},
]

SUB_LEVELS_DAYS_TO_EXPIRE = {
    SUB_LEVEL_FREE: None,
    SUB_LEVEL_PREMIUM: datetime.timedelta(days=30),
    SUB_LEVEL_PRO: datetime.timedelta(days=30),
    SUB_LEVEL_GOD: datetime.timedelta(days=365),
}


def get_subscriptions():
    """Returns subscription prices"""

    return SUBSCRIPTIONS


def sub_level_name(sub_level: int):
    for subscription in SUBSCRIPTIONS:
        if subscription["level"] == sub_level:
            return subscription["name"]

    raise MessageException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid subscription level"
    )


def create_wallet(uid: str):
    response = requests.post(
        f"{CREATE_WALLET_ENDPOINT}/{uid}", headers={"api_key": PAYMENTS_API_KEY}
    )

    if response.status_code != status.HTTP_200_OK:
        raise MessageException(status_code=response.status_code, detail=response.text)
    return response.json()["address"]


def get_expiration_date(sub_level: int, subscription_date: datetime.datetime):
    if SUB_LEVELS_DAYS_TO_EXPIRE[sub_level] is None:
        return None

    expiration_date = subscription_date + SUB_LEVELS_DAYS_TO_EXPIRE[sub_level]
    expiration_date = expiration_date.replace(minute=0, second=0, microsecond=0)
    return expiration_date


def get_sub_price(sub_level: int):
    """Returns the price of a subscription level"""

    for subscription in SUBSCRIPTIONS:
        if subscription["level"] == sub_level:
            return subscription["price"].upper()

    raise MessageException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid subscription level"
    )


def _make_payment(user: models.UserModel, sub_level: int):
    payment_response = requests.post(
        f"{DEPOSIT_ENDPOINT}/{user.id}",
        json={"amountInEthers": get_sub_price(sub_level)},
        headers={"api_key": PAYMENTS_API_KEY},
    )

    if payment_response.status_code != status.HTTP_200_OK:
        raise MessageException(
            status_code=payment_response.status_code, detail=payment_response.text
        )


def subscribe(user: models.UserModel, sub_level: int, pdb: Session) -> models.UserModel:
    if sub_level > SUB_LEVEL_FREE:
        _make_payment(user, sub_level)

    expiration_date = get_expiration_date(sub_level, datetime.datetime.now())

    return user.update(pdb, sub_level=sub_level, sub_expires=expiration_date)


def revoke_subscription(pdb: Session, now: datetime.datetime):
    users = models.UserModel.search(pdb, expiration_date=now, do_pagination=False)

    for user in users:
        user.update(
            pdb,
            sub_level=SUB_LEVEL_FREE,
            sub_expires=get_expiration_date(SUB_LEVEL_FREE, datetime.datetime.now()),
        )
