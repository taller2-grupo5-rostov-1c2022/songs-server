from ..album.base import AlbumBase


class Album(AlbumBase):
    cover: str
    score: float
    scores_amount: int
