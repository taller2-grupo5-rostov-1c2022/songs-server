from src.postgres import schemas
from src.postgres import models
from fastapi import APIRouter
from fastapi import Depends, Form, HTTPException
import json

from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres.models import AlbumModel, ArtistAlbumModel, SongModel

router = APIRouter(tags=["albums"])


@router.get("/albums/")
def get_albums(
    creator: str = None,
    pdb: Session = Depends(get_db),
):
    """Returns all Albums"""

    if creator is not None:
        albums = pdb.query(AlbumModel).filter(AlbumModel.creator == creator)
    else:
        albums = pdb.query(AlbumModel)

    return albums.all()


@router.get("/albums/{album_id}", response_model=schemas.AlbumBase)
def get_album_by_id(
    album_id: str,
    pdb: Session = Depends(get_db),
):
    """Returns an album by its id or 404 if not found"""
    album = pdb.query(AlbumModel).filter(AlbumModel.id == album_id).first()
    if album is None:
        raise HTTPException(status_code=404, detail=f"Album '{album}' not found")
    return album


@router.post("/albums/")
def post_album(
    user_id: str = Form(...),
    name: str = Form(...),
    description: str = Form(...),
    artists: str = Form(...),
    genre: str = Form(...),
    songs_ids: str = Form(...),
    pdb: Session = Depends(get_db),
):
    """Creates an album and returns its id. Songs_ids form is encoded like '["song_id_1", "song_id_2", ...]'"""

    songs = []
    for song_id in json.loads(songs_ids):
        song = pdb.query(SongModel).filter(SongModel.id == song_id).first()
        songs.append(song)

    artists_list = []
    for artist_name in json.loads(artists):
        artists_list.append(ArtistAlbumModel(artist_name=artist_name))

    album = models.AlbumModel(
        name=name,
        description=description,
        creator_id=user_id,
        genre=genre,
        artists=artists_list,
        songs=songs,
    )
    pdb.add(album)
    pdb.commit()
    return {"id": album.id}


@router.put("/albums/{album_id}")
def update_album(
    album_id: str,
    user_id: str = Form(...),
    name: str = Form(None),
    description: str = Form(None),
    artists: str = Form(None),
    genre: str = Form(None),
    songs_ids: str = Form(None),
    pdb: Session = Depends(get_db),
):
    """Updates album by its id"""
    # even though id is an integer, we can compare with a string
    album = pdb.query(AlbumModel).filter(AlbumModel.id == album_id).first()
    if album is None:
        raise HTTPException(status_code=404, detail=f"Song '{album_id}' not found")
    if album.creator_id != user_id:
        raise HTTPException(
            status_code=403,
            detail=f"User '{user_id} attempted to edit album of user with ID {album.creator_id}",
        )

    if name is not None:
        album.name = name
    if description is not None:
        album.description = description
    if artists is not None:
        album.artists = artists
    if genre is not None:
        album.genre = genre
    if songs_ids is not None:
        songs = []
        for song_id in songs_ids:
            # TODO: sacar codigo repetido con app/songs
            song = pdb.query(SongModel).filter(SongModel.id == song_id).first()

            songs.append(song)
        album.songs = songs

    pdb.commit()
    return {"id": album_id}


@router.delete("/albums/{album_id}")
def delete_album(
    user_id: str,
    album_id: str,
    pdb: Session = Depends(get_db),
):
    """Deletes an album by its id"""
    album = pdb.query(AlbumModel).filter(AlbumModel.id == album_id).first()
    if album is None:
        raise HTTPException(status_code=404, detail=f"Song '{album_id}' not found")

    if user_id != album.creator_id:
        raise HTTPException(
            status_code=403,
            detail=f"User '{user_id} attempted to delete album of user with ID {album.creator_id}",
        )
    pdb.query(AlbumModel).filter(AlbumModel.id == album_id).delete()
    pdb.commit()
