from sqlalchemy.orm import Session
from src.postgres.models import SongModel, ArtistModel
from fastapi import HTTPException
from src.postgres import schemas
from sqlalchemy import func
from .utils import ROLES_TABLE
from .. import roles


def create_song(pdb: Session, song: schemas.SongBase):
    db_song = SongModel(**song.dict())
    pdb.add(db_song)
    pdb.commit()
    pdb.refresh(db_song)
    return db_song


def get_songs(
    pdb: Session,
    role: str,
    creator_id: str = None,
    artist: str = None,
    genre: str = None,
    sub_level: int = None,
):
    if role not in ROLES_TABLE:
        raise HTTPException(status_code=422, detail=f"Invalid role: {role}")

    queries = []
    if ROLES_TABLE[role] < ROLES_TABLE["admin"]:
        queries.append(SongModel.blocked == False)

    if creator_id is not None:
        queries.append(SongModel.creator_id == creator_id)
    if artist is not None:
        queries.append(func.lower(ArtistModel.name).contains(artist.lower()))
    if genre is not None:
        queries.append(func.lower(SongModel.genre).contains(genre.lower()))
    if sub_level is not None:
        queries.append(SongModel.sub_level == sub_level)

    return pdb.query(SongModel).join(ArtistModel.songs).filter(*queries).all()


def get_song_by_id(pdb: Session, role: str, song_id: int):
    role_object = roles.Role(role)

    if role not in ROLES_TABLE:
        raise HTTPException(status_code=422, detail=f"Invalid role: {role}")

    song = pdb.query(SongModel).filter(SongModel.id == song_id).first()
    if song is None:
        raise HTTPException(
            status_code=404,
            detail=f"Song '{str(song_id)}' not found",
        )

    print(song.blocked, role)
    if song.blocked and ROLES_TABLE[role] < ROLES_TABLE["admin"]:
        raise HTTPException(status_code=403, detail=f"Song is blocked")

    return song
