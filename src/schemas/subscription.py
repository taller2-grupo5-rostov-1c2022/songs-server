from pydantic import BaseModel


class SubscriptionBase(BaseModel):
    level: int
    name: str
    price: str
