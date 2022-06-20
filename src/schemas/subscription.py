from pydantic import BaseModel


__all__ = ["SubscriptionBase"]


class SubscriptionBase(BaseModel):
    level: int
    name: str
    price: str
