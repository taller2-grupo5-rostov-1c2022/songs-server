from src import roles
from src.postgres import schemas
from fastapi import APIRouter
from fastapi import Depends, Form, HTTPException
from typing import List
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres import models
from src.repositories import playlist_utils, user_utils
from src.roles import get_role

router = APIRouter(tags=["playlists"])


@router.get("/playlists/", response_model=List[schemas.PlaylistBase])
def get_playlists(
    colab: str = None,
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
):
    """Returns playlists either filtered by colab or all playlists"""

    return playlist_utils.get_playlists(pdb, role, colab)


@router.get("/my_playlists/", response_model=List[schemas.PlaylistBase])
def get_my_playlists(
    uid: str = Depends(user_utils.retrieve_uid), pdb: Session = Depends(get_db)
):
    return playlist_utils.get_playlists(pdb, roles.Role.admin(), uid)


@router.get("/playlists/{playlist_id}", response_model=schemas.PlaylistBase)
def get_playlist_by_id(
    playlist_id: int,
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
):
    """Returns a playlist by its id or 404 if not found"""

    playlist = playlist_utils.get_playlist_by_id(pdb, role, playlist_id)

    return playlist


@router.post("/playlists/", response_model=schemas.PlaylistBase)
def post_playlist(
    playlist_info: schemas.PlaylistPost = Depends(playlist_utils.retrieve_playlist),
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
):
    """Creates a playlist and returns its id. Songs_ids form is encoded like '["song_id_1", "song_id_2", ...]'.
    Colabs_ids form is encoded like '["colab_id_1", "colab_id_2", ...]'"""

    songs = playlist_utils.get_songs_list(pdb, role, playlist_info.songs_ids)
    colabs = playlist_utils.get_colabs_list(pdb, playlist_info.colabs_ids)

    playlist = models.PlaylistModel(
        **playlist_info.dict(exclude={"songs_ids", "colabs_ids"}),
        colabs=colabs,
        songs=songs,
    )
    pdb.add(playlist)
    pdb.commit()

    return playlist


@router.put("/playlists/{playlist_id}")
def update_playlist(
    playlist_id: int,
    uid: str = Depends(user_utils.retrieve_uid),
    role: roles.Role = Depends(get_role),
    playlist_update: schemas.PlaylistUpdate = Depends(
        playlist_utils.retrieve_playlist_update
    ),
    pdb: Session = Depends(get_db),
):
    """Updates playlist by its id"""
    # even though id is an integer, we can compare with a string
    playlist = pdb.get(models.PlaylistModel, playlist_id)
    if playlist is None:
        raise HTTPException(
            status_code=404, detail=f"Playlist '{playlist_id}' not found"
        )

    if (
        uid not in [colab.id for colab in playlist.colabs]
        and uid != playlist.creator_id
        and not role.can_edit_everything()
    ):
        raise HTTPException(
            status_code=403,
            detail=f"User '{uid} attempted to edit playlist in which is not a collaborator",
        )

    playlist_update = playlist_update.dict()

    for playlist_attr in playlist_update:
        if playlist_update[playlist_attr] is not None:
            setattr(playlist, playlist_attr, playlist_update[playlist_attr])

    if playlist_update["colabs_ids"] is not None:
        colabs = playlist_utils.get_colabs_list(pdb, playlist_update["colabs_ids"])
        playlist.colabs = colabs

    if playlist_update["songs_ids"] is not None:
        songs = playlist_utils.get_songs_list(pdb, role, playlist_update["songs_ids"])
        playlist.songs = songs

    if playlist_update["blocked"] is not None:
        if not role.can_block():
            raise HTTPException(
                status_code=403,
                detail=f"User {uid} without permissions tried to block playlist {playlist.id}",
            )
        playlist.blocked = playlist_update["blocked"]

    pdb.commit()


@router.delete("/playlists/{playlist_id}")
def delete_playlist(
    playlist_id: str,
    uid: str = Depends(user_utils.retrieve_uid),
    pdb: Session = Depends(get_db),
):
    """Deletes a playlist by its id"""
    playlist = (
        pdb.query(models.PlaylistModel)
        .filter(models.PlaylistModel.id == playlist_id)
        .first()
    )
    if playlist is None:
        raise HTTPException(
            status_code=404, detail=f"Playlist '{playlist_id}' not found"
        )

    if uid != playlist.creator_id:
        raise HTTPException(
            status_code=403,
            detail=f"User '{uid} attempted to delete playlist of user with ID {playlist.creator_id}",
        )
    pdb.query(models.PlaylistModel).filter(
        models.PlaylistModel.id == playlist_id
    ).delete()
    pdb.commit()


@router.post("/playlists/{playlist_id}/songs/")
def add_song_to_playlist(
    playlist_id: str,
    song_id: str = Form(...),
    uid: str = Depends(user_utils.retrieve_uid),
    pdb: Session = Depends(get_db),
):
    """Adds a song to a playlist"""
    playlist = (
        pdb.query(models.PlaylistModel)
        .filter(models.PlaylistModel.id == playlist_id)
        .first()
    )

    if playlist is None:
        raise HTTPException(
            status_code=404, detail=f"Playlist '{playlist_id}' not found"
        )

    if uid != playlist.creator_id and uid not in [
        colab.id for colab in playlist.colabs
    ]:
        raise HTTPException(
            status_code=403,
            detail=f"User {uid} attempted to add a song to playlist of user with ID {playlist.creator_id}",
        )

    song = pdb.query(models.SongModel).filter(models.SongModel.id == song_id).first()
    if song is None:
        raise HTTPException(status_code=404, detail=f"Song '{song_id}' not found")

    playlist.songs.append(song)
    pdb.commit()

    return {"id": playlist_id}


@router.delete("/playlists/{playlist_id}/songs/{song_id}/")
def remove_song_from_playlist(
    playlist_id: str,
    song_id: str,
    uid: str = Depends(user_utils.retrieve_uid),
    pdb: Session = Depends(get_db),
):
    """Removes a song from a playlist"""
    playlist = (
        pdb.query(models.PlaylistModel)
        .filter(models.PlaylistModel.id == playlist_id)
        .first()
    )

    if playlist is None:
        raise HTTPException(
            status_code=404, detail=f"Playlist '{playlist_id}' not found"
        )

    if uid != playlist.creator_id and uid not in [
        colab.id for colab in playlist.colabs
    ]:
        raise HTTPException(
            status_code=403,
            detail=f"User {uid} attempted to remove a song from playlist of user with ID {playlist.creator_id}",
        )

    song = pdb.query(models.SongModel).filter(models.SongModel.id == song_id).first()
    if song is None:
        raise HTTPException(status_code=404, detail=f"Song '{song_id}' not found")

    playlist.songs.remove(song)
    pdb.commit()


@router.post("/playlists/{playlist_id}/colabs/")
def add_colab_to_playlist(
    playlist_id: str,
    colab_id: str = Form(...),
    uid: str = Depends(user_utils.retrieve_uid),
    pdb: Session = Depends(get_db),
):
    """Adds a song to a playlist"""
    playlist = (
        pdb.query(models.PlaylistModel)
        .filter(models.PlaylistModel.id == playlist_id)
        .first()
    )

    if playlist is None:
        raise HTTPException(
            status_code=404, detail=f"Playlist '{playlist_id}' not found"
        )

    if uid != playlist.creator_id:
        raise HTTPException(
            status_code=403,
            detail=f"User {uid} attempted to add a song to playlist of user with ID {playlist.creator_id}",
        )

    colab = pdb.query(models.UserModel).filter(models.UserModel.id == colab_id).first()
    if colab is None:
        raise HTTPException(status_code=404, detail=f"Song '{colab_id}' not found")

    playlist.colabs.append(colab)
    pdb.commit()

    return {"id": playlist_id}
