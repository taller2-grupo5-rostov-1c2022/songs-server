from sqlalchemy.orm import Session
from src.postgres import schemas
from src.postgres.models import SongModel
from typing import Optional
from fastapi import HTTPException
from src.postgres import schemas


def create_song(pdb: Session, song: schemas.SongBase):
    db_song = SongModel(**song.dict())
    pdb.add(db_song)
    pdb.commit()
    pdb.refresh(db_song)
    return db_song


def get_songs(pdb: Session, creator_id: Optional[str]):
    if creator_id is not None:
        return pdb.query(SongModel).filter(SongModel.creator_id == creator_id).all()
    else:
        return pdb.query(SongModel).all()


def get_song_by_id(pdb: Session, song_id: int) -> schemas.SongBase:
    try:
        song = pdb.query(SongModel).filter(SongModel.id == song_id).first()
        song_schema = schemas.SongBase(**song.__dict__.copy(), artists=song.artists)

        return song_schema
    except Exception as entry_not_found:
        raise HTTPException(
            status_code=404,
            detail=f"Song '{str(song_id)}' not found",
        ) from entry_not_found
