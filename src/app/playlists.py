from src import roles, utils, schemas
from fastapi import Depends, HTTPException, status, APIRouter
from typing import List
from sqlalchemy.orm import Session
from src.database.access import get_db
from src.database import models, crud
from src.roles import get_role

router = APIRouter(tags=["playlists"])


@router.get("/playlists/", response_model=List[schemas.PlaylistBase])
def get_playlists(
    colab: str = None,
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
):
    """Returns playlists either filtered by colab or all playlists"""

    return crud.playlist.get_playlists(
        pdb, role.can_see_blocked(), role.can_see_blocked(), colab
    )


@router.get("/my_playlists/", response_model=List[schemas.PlaylistBase])
def get_my_playlists(
    uid: str = Depends(utils.user.retrieve_uid), pdb: Session = Depends(get_db)
):
    return crud.playlist.get_playlists(
        pdb, show_blocked_songs=True, show_blocked_playlists=True, colab_id=uid
    )


@router.get("/playlists/{playlist_id}", response_model=schemas.Playlist)
def get_playlist_by_id(
    playlist: models.PlaylistModel = Depends(utils.playlist.get_playlist),
):
    """Returns a playlist by its id or 404 if not found"""

    return playlist


@router.post("/playlists/", response_model=schemas.PlaylistBase)
def post_playlist(
    playlist_info: schemas.PlaylistPost = Depends(utils.playlist.retrieve_playlist),
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
):
    """Creates a playlist and returns its id. Songs_ids form is encoded like '["song_id_1", "song_id_2", ...]'.
    Colabs_ids form is encoded like '["colab_id_1", "colab_id_2", ...]'"""

    playlist = crud.playlist.create_playlist(pdb, playlist_info, role.can_see_blocked())

    return playlist


@router.put("/playlists/{playlist_id}")
def update_playlist(
    playlist: models.PlaylistModel = Depends(utils.playlist.get_playlist),
    role: roles.Role = Depends(get_role),
    playlist_update: schemas.PlaylistUpdate = Depends(
        utils.playlist.retrieve_playlist_update
    ),
    pdb: Session = Depends(get_db),
    uid: str = Depends(utils.user.retrieve_uid),
):
    """Updates playlist by its id"""

    if not utils.playlist.can_edit_playlist(playlist, role, uid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can't edit this playlist"
        )

    crud.playlist.update_playlist(
        pdb, playlist, playlist_update, role.can_see_blocked(), role.can_block()
    )


@router.delete("/playlists/{playlist_id}")
def delete_playlist(
    playlist: models.PlaylistModel = Depends(utils.playlist.get_playlist),
    uid: str = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
    role: roles.Role = Depends(get_role),
):
    """Deletes a playlist by its id"""

    if playlist.creator_id != uid and not role.can_edit_everything():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User '{uid} attempted to delete playlist of user with ID {playlist.creator_id}",
        )
    crud.playlist.delete_playlist(pdb, playlist)


@router.delete("/playlists/{playlist_id}/songs/{song_id}/")
def remove_song_from_playlist(
    song: models.SongModel = Depends(utils.song.get_song),
    playlist: models.PlaylistModel = Depends(utils.playlist.get_playlist),
    uid: str = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
    role: roles.Role = Depends(get_role),
):
    """Removes a song from a playlist"""

    if not utils.playlist.can_edit_playlist(playlist, role, uid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can't edit this playlist"
        )

    crud.playlist.remove_song(pdb, playlist, song)


@router.post("/playlists/{playlist_id}/songs/")
def add_song_to_playlist(
    song: models.SongModel = Depends(utils.song.get_song_from_form),
    playlist: models.PlaylistModel = Depends(utils.playlist.get_playlist),
    uid: str = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
    role: roles.Role = Depends(get_role),
):
    """Adds a song to a playlist"""

    if not utils.playlist.can_edit_playlist(playlist, role, uid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can't edit this playlist"
        )

    crud.playlist.add_song(pdb, playlist, song)

    return {"id": playlist.id}


@router.post("/playlists/{playlist_id}/colabs/")
def add_colab_to_playlist(
    playlist: models.PlaylistModel = Depends(utils.playlist.get_playlist),
    colab: models.UserModel = Depends(utils.playlist.get_colab_from_form),
    uid: str = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
):
    """Adds a song to a playlist"""

    if uid != playlist.creator_id:
        raise HTTPException(
            status_code=403,
            detail=f"User {uid} attempted to add a colab to playlist of user with ID {playlist.creator_id}",
        )

    crud.playlist.add_colab(pdb, playlist, colab)

    return {"id": playlist.id}
