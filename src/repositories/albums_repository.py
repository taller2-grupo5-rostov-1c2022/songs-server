from sqlalchemy.orm import Session, joinedload
from src.postgres.models import AlbumModel, ArtistModel, SongModel
from fastapi import HTTPException
from sqlalchemy import func
from .utils import ROLES_TABLE
from .. import roles


def get_albums(
    pdb: Session,
    role: roles.Role,
    creator_id: str = None,
    artist: str = None,
    genre: str = None,
    sub_level: int = None,
):
    queries = []
    if not role.can_see_blocked():
        # This action should not be committed
        pdb.query(SongModel).filter(SongModel.blocked == True).delete()
        queries.append(AlbumModel.blocked == False)

    if creator_id is not None:
        queries.append(AlbumModel.album_creator_id == creator_id)
    if artist is not None:
        queries.append(func.lower(ArtistModel.name).contains(artist.lower()))
    if genre is not None:
        queries.append(func.lower(AlbumModel.genre).contains(genre.lower()))
    if sub_level is not None:
        queries.append(AlbumModel.sub_level == sub_level)

    results = pdb.query(AlbumModel).join(ArtistModel.songs, full=True).join(SongModel.album, full=True).filter(*queries).all()

    return results


def get_album_by_id(pdb: Session, role: roles.Role, album_id: int):
    queries = []
    if not role.can_see_blocked():
        # This action should not be committed
        pdb.query(SongModel).filter(SongModel.blocked == True).delete()
        queries.append(AlbumModel.blocked == False)

    album = (
        pdb.query(AlbumModel)
        .options(joinedload(AlbumModel.songs))
        .filter(AlbumModel.id == album_id)
        .first()
    )

    if album is None:
        raise HTTPException(
            status_code=404,
            detail=f"Album '{str(album_id)}' not found",
        )
    if album.blocked and not role.can_see_blocked():
        raise HTTPException(status_code=403, detail=f"Album is blocked")

    return album
