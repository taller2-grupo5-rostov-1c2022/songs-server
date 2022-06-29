from fastapi import Depends
from sqlalchemy.orm import Session

from src.database.access import get_db
from src import utils
from src.database import models


def get_review(
    album: models.AlbumModel = Depends(utils.album.get_album),
    pdb: Session = Depends(get_db),
    user: models.UserModel = Depends(utils.user.retrieve_user),
):
    reviews = models.ReviewModel.get(pdb, album=album, reviewer=user)

    return reviews
