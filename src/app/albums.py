from src.postgres import schemas
from src.postgres import models
from fastapi import APIRouter
from fastapi import Depends, Form, HTTPException, UploadFile, File, Header
from src.firebase.access import get_bucket
from src.crud import albums as crud_albums
import json

from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres.models import AlbumModel, SongModel

router = APIRouter(tags=["albums"])


@router.get("/albums/")
def get_albums(
    creator: str = None,
    pdb: Session = Depends(get_db),
):
    """Returns all Albums"""

    return crud_albums.get_albums(pdb, creator)


@router.get("/my_albums/")
def get_my_albums(uid: str = Header(...), pdb: Session = Depends(get_db)):
    return crud_albums.get_albums(pdb, uid)


@router.get("/albums/{album_id}", response_model=schemas.AlbumGet)
def get_album_by_id(
    album_id: str, pdb: Session = Depends(get_db), bucket=Depends(get_bucket)
):
    """Returns an album by its id or 404 if not found"""

    album = crud_albums.get_album_by_id(pdb, album_id).__dict__

    blob = bucket.blob("albums/" + str(album_id))
    blob.make_public()

    album["cover"] = blob.public_url

    return album


@router.post("/albums/")
def post_album(
    uid: str = Form(...),
    name: str = Form(...),
    description: str = Form(...),
    genre: str = Form(...),
    songs_ids: str = Form(...),
    sub_level: int = Form(...),
    cover: UploadFile = File(...),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Creates an album and returns its id. Songs_ids form is encoded like '["song_id_1", "song_id_2", ...]'"""

    songs = []
    for song_id in json.loads(songs_ids):
        song = pdb.query(SongModel).filter(SongModel.id == song_id).first()
        songs.append(song)

    album = models.AlbumModel(
        name=name,
        description=description,
        creator_id=uid,
        genre=genre,
        sub_level=sub_level,
        songs=songs,
    )
    pdb.add(album)
    pdb.commit()

    blob = bucket.blob(f"covers/{album.id}")
    blob.upload_from_file(cover)

    return {"id": album.id}


@router.put("/albums/{album_id}")
def update_album(
    album_id: str,
    uid: str = Form(...),
    name: str = Form(None),
    description: str = Form(None),
    genre: str = Form(None),
    songs_ids: str = Form(None),
    sub_level: int = Form(None),
    cover: UploadFile = File(None),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Updates album by its id"""
    # even though id is an integer, we can compare with a string
    album = pdb.query(AlbumModel).filter(AlbumModel.id == album_id).first()
    if album is None:
        raise HTTPException(status_code=404, detail=f"Album '{album_id}' not found")
    if album.creator_id != uid:
        raise HTTPException(
            status_code=403,
            detail=f"User '{uid} attempted to edit album of user with ID {album.creator_id}",
        )

    if name is not None:
        album.name = name
    if description is not None:
        album.description = description
    if genre is not None:
        album.genre = genre
    if sub_level is not None:
        album.sub_level = sub_level

    if cover is not None:
        try:
            blob = bucket.blob("covers/" + album_id)
            blob.upload_from_file(cover.file)
        except Exception as entry_not_found:
            raise HTTPException(
                status_code=404, detail=f"Files for Cover '{album_id}' not found"
            ) from entry_not_found

    if songs_ids is not None:
        songs = []
        for song_id in json.loads(songs_ids):
            # TODO: sacar codigo repetido con app/songs
            song = pdb.query(SongModel).filter(SongModel.id == song_id).first()

            songs.append(song)
        album.songs = songs

    pdb.commit()
    return {"id": album_id}


@router.delete("/albums/{album_id}")
def delete_album(
    uid: str,
    album_id: str,
    pdb: Session = Depends(get_db),
):
    """Deletes an album by its id"""
    album = pdb.query(AlbumModel).filter(AlbumModel.id == album_id).first()
    if album is None:
        raise HTTPException(status_code=404, detail=f"Album '{album_id}' not found")

    if uid != album.creator_id:
        raise HTTPException(
            status_code=403,
            detail=f"User '{uid} attempted to delete album of user with ID {album.creator_id}",
        )
    pdb.query(AlbumModel).filter(AlbumModel.id == album_id).delete()
    pdb.commit()
