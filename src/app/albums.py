from src.postgres import schemas
from src.postgres import models
from fastapi import APIRouter
from fastapi import Depends, Form, HTTPException, UploadFile, File, Header
from src.firebase.access import get_bucket
from src.repositories import albums_repository as crud_albums
from typing import List
import json
import datetime
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
    bucket=Depends(get_bucket),
):
    """Returns all Albums"""

    albums = crud_albums.get_albums(pdb, creator, artist, genre, sub_level)

    for album in albums:
        blob = bucket.blob("covers/" + str(album.id))
        album.cover = (
            blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(days=1),
                method="GET",
            )
            + "?t="
            + str(album.cover_last_update)
        )

    return albums


@router.get("/my_albums/", response_model=List[schemas.AlbumGet])
def get_my_albums(
    uid: str = Header(...),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):

    albums = crud_albums.get_albums(pdb, uid)

    for album in albums:
        blob = bucket.blob("covers/" + str(album.id))
        album.cover = (
            blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(days=1),
                method="GET",
            )
            + "?t="
            + str(album.cover_last_update)
        )

    return albums


@router.get("/albums/{album_id}", response_model=schemas.AlbumGet)
def get_album_by_id(
    album_id: int, pdb: Session = Depends(get_db), bucket=Depends(get_bucket)
):
    """Returns an album by its id or 404 if not found"""

    album = crud_albums.get_album_by_id(pdb, album_id)

    blob = bucket.blob("covers/" + str(album_id))
    album.cover = (
        blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(days=1),
            method="GET",
        )
        + "?t="
        + str(album.cover_last_update)
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

    blob = bucket.blob(f"covers/{album.id}")
    blob.upload_from_file(cover.file)

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

    pdb.commit()

    if cover is not None:
        try:
            blob = bucket.blob("covers/" + album_id)
            blob.upload_from_file(cover.file)
            album.cover_last_update = datetime.datetime.now()

        except Exception as entry_not_found:
            raise HTTPException(
                status_code=404, detail=f"Files for Cover '{album_id}' not found"
            ) from entry_not_found

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
    return {"id": album_id}


@router.delete("/albums/{album_id}")
def delete_album(
    uid: str, album_id: int, pdb: Session = Depends(get_db), bucket=Depends(get_bucket)
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
    bucket.blob("covers/" + str(album_id)).delete()
    pdb.commit()
