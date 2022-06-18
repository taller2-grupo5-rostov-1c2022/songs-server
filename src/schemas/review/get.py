from .base import ReviewBase
from ..user.base import UserBase


class ReviewGet(ReviewBase):
    reviewer: UserBase
