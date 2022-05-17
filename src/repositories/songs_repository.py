from sqlalchemy.orm import Session
from src.postgres.models import SongModel, ArtistModel
from fastapi import HTTPException
from src.postgres import schemas
from sqlalchemy import func
from .. import roles


def create_song(pdb: Session, song: schemas.SongBase):
    db_song = SongModel(**song.dict())
    pdb.add(db_song)
    pdb.commit()
    pdb.refresh(db_song)
    return db_song


def get_songs(
    pdb: Session,
    role: roles.Role,
    creator_id: str = None,
    artist: str = None,
    genre: str = None,
    sub_level: int = None,
):
    queries = []
    if not role.can_see_blocked():
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


def get_song_by_id(pdb: Session, role: roles.Role, song_id: int):
    song = pdb.query(SongModel).filter(SongModel.id == song_id).first()
    if song is None:
        raise HTTPException(
            status_code=404,
            detail=f"Song '{str(song_id)}' not found",
        )

    if song.blocked and not role.can_see_blocked():
        raise HTTPException(status_code=403, detail=f"Song is blocked")

    return song
