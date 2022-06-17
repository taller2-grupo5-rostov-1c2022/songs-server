from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src import schemas, roles
from src.database import models


def update_album(
    pdb: Session,
    album: models.AlbumModel,
    album_update: schemas.AlbumUpdate,
    role: roles.Role,
):
    blocked = album_update.blocked
    songs_ids = album_update.songs_ids
    album_update = album_update.dict(
        exclude_none=True, exclude={"blocked", "songs_ids"}
    )

    for album_attr in album_update:
        setattr(album, album_attr, album_update[album_attr])
    if songs_ids is not None:
        album.songs = models.SongModel.get_many(pdb, ids=songs_ids, role=role)

    if blocked:
        if not role.can_block():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You can't block albums"
            )

        album.blocked = blocked

    pdb.commit()


def delete_album(
    pdb: Session,
    album: models.AlbumModel,
):
    pdb.delete(album)
    pdb.commit()
