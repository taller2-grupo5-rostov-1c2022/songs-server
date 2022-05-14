from sqlalchemy.orm import Session
from src.postgres.models import SongModel, ArtistModel
from fastapi import HTTPException
from src.postgres import schemas
from sqlalchemy import func


def create_song(pdb: Session, song: schemas.SongBase):
    db_song = SongModel(**song.dict())
    pdb.add(db_song)
    pdb.commit()
    pdb.refresh(db_song)
    return db_song


def get_songs(
    pdb: Session,
    creator_id: str = None,
    artist: str = None,
    genre: str = None,
    sub_level: int = None,
):
    queries = []
    if creator_id is not None:
        queries.append(SongModel.creator_id == creator_id)
    if artist is not None:
        queries.append(func.lower(ArtistModel.name).contains(artist.lower()))
    if genre is not None:
        queries.append(func.lower(SongModel.genre).contains(genre.lower()))
    if sub_level is not None:
        queries.append(SongModel.sub_level == sub_level)

    return pdb.query(SongModel).join(ArtistModel.songs).filter(*queries).all()


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
