from src import roles, utils, schemas
from src.database.access import get_db
from typing import List
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from src.database import models, crud

router = APIRouter(tags=["favorites"])


@router.get("/users/{uid}/favorites/songs/", response_model=List[schemas.SongBase])
def get_favorite_songs(
    user: models.UserModel = Depends(utils.user.retrieve_user),
    role: roles.Role = Depends(roles.get_role),
):
    return crud.user.get_favorite_songs(user, role.can_see_blocked())


@router.post("/users/{uid}/favorites/songs/", response_model=schemas.SongBase)
def add_song_to_favorites(
    song: models.SongModel = Depends(utils.song.get_song),
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
):
    return crud.user.add_song_to_favorites(pdb, user, song)


@router.delete("/users/{uid}/favorites/songs/")
def remove_song_from_favorites(
    song: models.SongModel = Depends(utils.song.get_song),
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
):
    return crud.user.remove_song_from_favorites(pdb, user, song)


@router.get("/users/{uid}/favorites/albums/", response_model=List[schemas.AlbumGet])
def get_favorite_albums(
    user: models.UserModel = Depends(utils.user.retrieve_user),
    role: roles.Role = Depends(roles.get_role),
    pdb: Session = Depends(get_db),
):
    favorite_albums = crud.user.get_favorite_albums(
        user, role.can_see_blocked(), role.can_see_blocked()
    )

    for album in favorite_albums:
        album.cover = utils.album.cover_url(album)
        album.score = utils.album.calculate_score(pdb, album)
        album.scores_amount = utils.album.calculate_scores_amount(pdb, album)

    return favorite_albums


@router.post("/users/{uid}/favorites/albums/", response_model=schemas.AlbumBase)
def add_album_to_favorites(
    album: models.AlbumModel = Depends(utils.album.get_album),
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
):
    return crud.user.add_album_to_favorites(pdb, user, album)


@router.delete("/users/{uid}/favorites/albums/")
def remove_album_from_favorites(
    album: models.AlbumModel = Depends(utils.album.get_album),
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
):
    return crud.user.remove_album_from_favorites(pdb, user, album)


@router.get(
    "/users/{uid}/favorites/playlists/", response_model=List[schemas.PlaylistBase]
)
def get_favorite_playlists(
    user: models.UserModel = Depends(utils.user.retrieve_user),
    role: roles.Role = Depends(roles.get_role),
    pdb: Session = Depends(get_db),
):
    return crud.user.get_favorite_playlists(pdb, user, role.can_see_blocked(), role.can_see_blocked())


@router.post(
    "/users/{uid}/favorites/playlists/",
    response_model=schemas.PlaylistBase,
)
def add_playlist_to_favorites(
    playlist: models.PlaylistModel = Depends(utils.playlist.get_playlist),
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
):
    return crud.user.add_playlist_to_favorites(pdb, user, playlist)


@router.delete("/users/{uid}/favorites/playlists/")
def remove_playlist_from_favorites(
    playlist: models.PlaylistModel = Depends(utils.playlist.get_playlist),
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
):
    return crud.user.remove_playlist_from_favorites(pdb, user, playlist)
