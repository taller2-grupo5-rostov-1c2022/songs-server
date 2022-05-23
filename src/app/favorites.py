from src import roles
from src.constants import STORAGE_PATH, SUPPRESS_BLOB_ERRORS
from src.postgres import schemas
from typing import List
from fastapi import APIRouter
from fastapi import Depends, HTTPException, Form, Header, UploadFile
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.firebase.access import get_bucket, get_auth
from src.postgres import models
import datetime

from src.repositories import (
    user_utils,
    comment_utils,
    song_utils,
    album_utils,
    playlist_utils,
)

router = APIRouter(tags=["favorites"])


@router.get("/users/{uid}/favorites/songs/", response_model=List[schemas.SongBase])
def get_favorite_songs(
    uid: str = Depends(user_utils.retrieve_uid),
    role: roles.Role = Depends(roles.get_role),
    pdb: Session = Depends(get_db),
):
    return user_utils.get_favorite_songs(pdb, uid, role)


@router.post("/users/{uid}/favorites/songs/", response_model=schemas.SongBase)
def add_song_to_favorites(
    song: models.SongModel = Depends(song_utils.get_song),
    user: models.UserModel = Depends(user_utils.get_user),
    pdb: Session = Depends(get_db),
):
    return user_utils.add_song_to_favorites(pdb, user, song)


@router.delete("/users/{uid}/favorites/songs/")
def remove_song_from_favorites(
    song: models.SongModel = Depends(song_utils.get_song),
    user: models.UserModel = Depends(user_utils.get_user),
    pdb: Session = Depends(get_db),
):
    return user_utils.remove_song_from_favorites(pdb, user, song)


@router.get("/users/{uid}/favorites/albums/", response_model=List[schemas.AlbumGet])
def get_favorite_albums(
    uid: str = Depends(user_utils.retrieve_uid),
    role: roles.Role = Depends(roles.get_role),
    pdb: Session = Depends(get_db),
):
    favorite_albums = user_utils.get_favorite_albums(pdb, uid, role)
    for album in favorite_albums:
        album.cover = album_utils.cover_url(album)
        album.score = album_utils.calculate_score(pdb, album)
        album.scores_amount = album_utils.calculate_scores_amount(pdb, album)

    return favorite_albums


@router.post("/users/{uid}/favorites/albums/", response_model=schemas.AlbumBase)
def add_album_to_favorites(
    album: models.AlbumModel = Depends(album_utils.get_album),
    user: models.UserModel = Depends(user_utils.get_user),
    pdb: Session = Depends(get_db),
):
    return user_utils.add_album_to_favorites(pdb, user, album)


@router.delete("/users/{uid}/favorites/albums/")
def remove_album_from_favorites(
    album: models.AlbumModel = Depends(album_utils.get_album),
    user: models.UserModel = Depends(user_utils.get_user),
    pdb: Session = Depends(get_db),
):
    return user_utils.remove_album_from_favorites(pdb, user, album)


@router.get(
    "/users/{uid}/favorites/playlists/", response_model=List[schemas.PlaylistBase]
)
def get_favorite_playlists(
    uid: str = Depends(user_utils.retrieve_uid),
    role: roles.Role = Depends(roles.get_role),
    pdb: Session = Depends(get_db),
):
    return user_utils.get_favorite_playlists(pdb, uid, role)


@router.post(
    "/users/{uid}/favorites/playlists/",
    response_model=schemas.PlaylistBase,
)
def add_playlist_to_favorites(
    playlist: models.PlaylistModel = Depends(playlist_utils.get_playlist),
    user: models.UserModel = Depends(user_utils.get_user),
    pdb: Session = Depends(get_db),
):
    return user_utils.add_playlist_to_favorites(pdb, user, playlist)
