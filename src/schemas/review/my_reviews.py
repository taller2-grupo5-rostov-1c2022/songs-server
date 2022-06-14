from .base import ReviewBase
from ..album.base import AlbumBase


class ReviewMyReviews(ReviewBase):
    album: AlbumBase
