import datetime
from src.postgres import schemas
from src.postgres import models
from src.constants import STORAGE_PATH, SUPPRESS_BLOB_ERRORS
from fastapi import APIRouter
from fastapi import Depends, Form, HTTPException, UploadFile, File, Header
from src.firebase.access import get_bucket
from src.repositories import albums_repository as crud_albums
from typing import List
import json
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres.models import AlbumModel, SongModel, UserModel

router = APIRouter(tags=["albums"])


@router.get("/albums/", response_model=List[schemas.AlbumGet])
def get_albums(
    creator: str = None,
    artist: str = None,
    genre: str = None,
    sub_level: int = None,
    pdb: Session = Depends(get_db),
):
    """Returns all Albums"""

    albums = crud_albums.get_albums(pdb, creator, artist, genre, sub_level)

    for album in albums:
        album.cover = (
            STORAGE_PATH
            + "covers/"
            + str(album.id)
            + "?t="
            + str(album.cover_last_update)
        )

    return albums


@router.get("/my_albums/", response_model=List[schemas.AlbumGet])
def get_my_albums(
    uid: str = Header(...),
    pdb: Session = Depends(get_db),
):

    albums = crud_albums.get_albums(pdb, uid)

    for album in albums:
        album.cover = (
            STORAGE_PATH
            + "covers/"
            + str(album.id)
            + "?t="
            + str(album.cover_last_update)
        )

    return albums


@router.get("/albums/{album_id}", response_model=schemas.AlbumGet)
def get_album_by_id(album_id: int, pdb: Session = Depends(get_db)):
    """Returns an album by its id or 404 if not found"""

    album = crud_albums.get_album_by_id(pdb, album_id)

    album.cover = (
        STORAGE_PATH + "covers/" + str(album_id) + "?t=" + str(album.cover_last_update)
    )

    return album


@router.post("/albums/")
def post_album(
    uid: str = Header(...),
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

    creator = pdb.query(UserModel).filter(UserModel.id == uid).first()
    if creator is None:
        raise HTTPException(status_code=404, detail=f"User with id {uid} not found")

    songs = []
    for song_id in json.loads(songs_ids):
        song = pdb.query(SongModel).filter(SongModel.id == song_id).first()
        if song.creator_id != uid:
            raise HTTPException(
                status_code=403,
                detail=f"User with id {uid} attempted to create an album with songs of user with id {song.creator_id}",
            )
        songs.append(song)

    album = models.AlbumModel(
        name=name,
        description=description,
        album_creator=creator,
        genre=genre,
        sub_level=sub_level,
        cover_last_update=datetime.datetime.now(),
        songs=songs,
    )
    pdb.add(album)
    pdb.commit()

    for song in songs:
        song.album = album
        pdb.refresh(song)

    try:
        blob = bucket.blob(f"covers/{album.id}")
        blob.upload_from_file(cover.file)
        blob.make_public()
        album.cover_last_update = datetime.datetime.now()
        pdb.commit()
    except Exception as entry_not_found:
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507, detail=f"Could not upload cover for album {album.id}"
            ) from entry_not_found

    return {"id": album.id}


@router.put("/albums/{album_id}")
def update_album(
    album_id: str,
    uid: str = Header(...),
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
    if album.album_creator_id != uid:
        raise HTTPException(
            status_code=403,
            detail=f"User '{uid} attempted to edit album of user with ID {album.album_creator_id}",
        )

    if name is not None:
        album.name = name
    if description is not None:
        album.description = description
    if genre is not None:
        album.genre = genre
    if sub_level is not None:
        album.sub_level = sub_level

    if songs_ids is not None:
        songs = []
        for song_id in json.loads(songs_ids):
            # TODO: sacar codigo repetido con app/songs
            song = pdb.query(SongModel).filter(SongModel.id == song_id).first()
            if song.creator_id != uid:
                raise HTTPException(
                    status_code=403,
                    detail=f"User with id {uid} attempted to update an album with songs of user with id {song.creator_id}",
                )

            songs.append(song)
        album.songs = songs

    pdb.commit()

    if cover is not None:
        try:
            blob = bucket.blob("covers/" + album_id)
            blob.upload_from_file(cover.file)
            album.cover_last_update = datetime.datetime.now()
            pdb.commit()
        except Exception as entry_not_found:
            if not SUPPRESS_BLOB_ERRORS:
                raise HTTPException(
                    status_code=507,
                    detail=f"Could not upload cover for album {album.id}",
                ) from entry_not_found

    return {"id": album_id}


@router.delete("/albums/{album_id}")
def delete_album(
    album_id: int,
    uid: str = Header(...),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Deletes an album by its id"""
    album = pdb.query(AlbumModel).filter(AlbumModel.id == album_id).first()
    if album is None:
        raise HTTPException(status_code=404, detail=f"Album '{album_id}' not found")

    if uid != album.album_creator_id:
        raise HTTPException(
            status_code=403,
            detail=f"User '{uid} attempted to delete album of user with ID {album.album_creator_id}",
        )
    pdb.query(AlbumModel).filter(AlbumModel.id == album_id).delete()
    pdb.commit()
    try:
        bucket.blob("covers/" + str(album_id)).delete()
    except Exception as entry_not_found:
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507, detail=f"Could not delete cover for album {album.id}"
            ) from entry_not_found
