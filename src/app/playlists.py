from src import roles, utils, schemas
from fastapi import Depends, HTTPException, status, APIRouter, Query
from sqlalchemy.orm import Session
from src.database.access import get_db
from src.database import models
from src.roles import get_role

from src.schemas.pagination import CustomPage

router = APIRouter(tags=["playlists"])


@router.get("/playlists/", response_model=CustomPage[schemas.PlaylistBase])
def get_playlists(
    colab: str = None,
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Returns playlists either filtered by colab or all playlists"""

    return models.PlaylistModel.search(
        pdb, role=role, colab=colab, limit=limit, offset=offset
    )


@router.get("/my_playlists/", response_model=CustomPage[schemas.PlaylistBase])
def get_my_playlists(
    uid: str = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    playlists = models.PlaylistModel.search(
        pdb, colab=uid, role=roles.Role.admin(), limit=limit, offset=offset
    )
    return playlists


@router.get("/playlists/{playlist_id}", response_model=schemas.PlaylistGet)
def get_playlist_by_id(
    playlist: models.PlaylistModel = Depends(utils.playlist.get_playlist),
):
    """Returns a playlist by its id or 404 if not found"""

    return playlist


@router.post("/playlists/", response_model=schemas.PlaylistBase)
def post_playlist(
    playlist_create: schemas.PlaylistCreate = Depends(utils.playlist.retrieve_playlist),
    role: roles.Role = Depends(get_role),
    pdb: Session = Depends(get_db),
):
    """Creates a playlist and returns its id. Songs_ids form is encoded like '["song_id_1", "song_id_2", ...]'.
    Colabs_ids form is encoded like '["colab_id_1", "colab_id_2", ...]'"""
    playlist = models.PlaylistModel.create(pdb, **playlist_create.dict(), role=role)

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

    playlist.update(pdb, **playlist_update.dict(exclude_none=True), role=role)


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
    playlist.delete(pdb)


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

    playlist.remove_song(pdb, song)


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

    playlist.add_song(pdb, song)

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

    playlist.add_colab(pdb, colab)

    return {"id": playlist.id}
