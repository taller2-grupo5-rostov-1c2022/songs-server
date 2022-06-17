from src import roles, utils, schemas
from src.database.access import get_db
from typing import List
from fastapi import APIRouter, status, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from src.database import models

router = APIRouter(tags=["favorites"])


@router.get("/users/{uid}/favorites/songs/", response_model=List[schemas.SongBase])
def get_favorite_songs(
    user: models.UserModel = Depends(utils.user.retrieve_user),
    role: roles.Role = Depends(roles.get_role),
):
    return user.get_favorite_songs(role=role)


@router.post("/users/{uid}/favorites/songs/", response_model=schemas.SongBase)
def add_song_to_favorites(
    song: models.SongModel = Depends(utils.song.get_song),
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
):
    if song in user.favorite_songs:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Song already in favorites"
        )
    user.add_favorite_song(pdb, song=song)
    return song


@router.delete("/users/{uid}/favorites/songs/")
def remove_song_from_favorites(
    song: models.SongModel = Depends(utils.song.get_song),
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
):
    if song not in user.favorite_songs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Song not in favorites"
        )
    user.remove_favorite_song(pdb, song=song)


@router.get("/users/{uid}/favorites/albums/", response_model=List[schemas.AlbumGet])
def get_favorite_albums(
    user: models.UserModel = Depends(utils.user.retrieve_user),
    role: roles.Role = Depends(roles.get_role),
    pdb: Session = Depends(get_db),
):
    favorite_albums = user.get_favorite_albums(role=role)

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
    if album in user.favorite_albums:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Album already in favorites"
        )
    user.add_favorite_album(pdb, album=album)
    return album


@router.delete("/users/{uid}/favorites/albums/")
def remove_album_from_favorites(
    album: models.AlbumModel = Depends(utils.album.get_album),
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
):
    if album not in user.favorite_albums:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Album not in favorites"
        )
    return user.remove_favorite_album(pdb, album=album)


@router.get(
    "/users/{uid}/favorites/playlists/", response_model=List[schemas.PlaylistBase]
)
def get_favorite_playlists(
    user: models.UserModel = Depends(utils.user.retrieve_user),
    role: roles.Role = Depends(roles.get_role),
):
    return user.get_favorite_playlists(role=role)


@router.post(
    "/users/{uid}/favorites/playlists/",
    response_model=schemas.PlaylistBase,
)
def add_playlist_to_favorites(
    playlist: models.PlaylistModel = Depends(utils.playlist.get_playlist),
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
):
    if playlist in user.favorite_playlists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Playlist already in favorites"
        )
    user.add_favorite_playlist(pdb, playlist=playlist)
    return playlist


@router.delete("/users/{uid}/favorites/playlists/")
def remove_playlist_from_favorites(
    playlist: models.PlaylistModel = Depends(utils.playlist.get_playlist),
    user: models.UserModel = Depends(utils.user.retrieve_user),
    pdb: Session = Depends(get_db),
):
    if playlist not in user.favorite_playlists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not in favorites"
        )
    return user.remove_favorite_playlist(pdb, playlist=playlist)
