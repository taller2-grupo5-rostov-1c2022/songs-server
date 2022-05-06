from src.postgres import schemas
from src.postgres import models
from fastapi import APIRouter
from fastapi import Depends, Form, HTTPException, Header
from src.firebase.access import get_bucket
from src.crud import playlists as crud_playlists
import json

from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres.models import PlaylistModel, SongModel, UserModel

router = APIRouter(tags=["playlists"])


@router.get("/playlists/")
def get_playlists(
    creator: str = None,
    pdb: Session = Depends(get_db),
):
    """Returns all playlists either filtered by creator or all playlists"""

    return crud_playlists.get_playlists(pdb, creator)


@router.get("/my_playlists/")
def get_my_playlists(uid: str = Header(...), pdb: Session = Depends(get_db)):
    return crud_playlists.get_playlists(pdb, uid)


@router.get("/playlists/{playlist_id}", response_model=schemas.PlaylistBase)
def get_playlist_by_id(playlist_id: str, pdb: Session = Depends(get_db)):
    """Returns a playlist by its id or 404 if not found"""

    playlist = crud_playlists.get_playlist_by_id(pdb, playlist_id).__dict__

    return playlist


@router.post("/playlists/")
def post_playlist(
    uid: str = Form(...),
    name: str = Form(...),
    description: str = Form(...),
    colabs_ids: str = Form(...),
    songs_ids: str = Form(...),
    pdb: Session = Depends(get_db),
):
    """Creates a playlist and returns its id. Songs_ids form is encoded like '["song_id_1", "song_id_2", ...]'.
    Colabs_ids form is encoded like '["colab_id_1", "colab_id_2", ...]'"""

    songs = []
    for song_id in json.loads(songs_ids):
        song = pdb.query(SongModel).filter(SongModel.id == song_id).first()
        songs.append(song)

    colabs = []
    for colab_id in json.loads(colabs_ids):
        colab = pdb.query(UserModel).filter(UserModel.id == colab_id).first()
        colabs.append(colab)

    playlist = models.PlaylistModel(
        name=name,
        description=description,
        creator_id=uid,
        colabs=colabs,
        songs=songs,
    )
    pdb.add(playlist)
    pdb.commit()

    return {"id": playlist.id}


@router.put("/playlists/{playlist_id}")
def update_playlist(
    playlist_id: str,
    uid: str = Form(...),
    name: str = Form(None),
    colabs_ids: str = Form(None),
    description: str = Form(None),
    songs_ids: str = Form(None),
    pdb: Session = Depends(get_db),
):
    """Updates playlist by its id"""
    # even though id is an integer, we can compare with a string
    playlist = pdb.query(PlaylistModel).filter(PlaylistModel.id == playlist_id).first()
    if playlist is None:
        raise HTTPException(
            status_code=404, detail=f"Playlist '{playlist_id}' not found"
        )
    print([colab.id for colab in playlist.colabs])
    if (
        uid not in [colab.id for colab in playlist.colabs]
        and uid != playlist.creator_id
    ):
        raise HTTPException(
            status_code=403,
            detail=f"User '{uid} attempted to edit playlist in which is not a collaborator",
        )

    if name is not None:
        playlist.name = name
    if description is not None:
        playlist.description = description
    if colabs_ids is not None:
        if uid != playlist.creator_id:
            raise HTTPException(
                status_code=403,
                detail=f"User '{uid} attempted to edit playlist collaborator in which is not the creator",
            )
        colabs = []
        for colab_id in json.loads(colabs_ids):
            colab = pdb.query(UserModel).filter(UserModel.id == colab_id).first()
            colabs.append(colab)
        playlist.colabs = colabs

    if songs_ids is not None:
        songs = []
        for song_id in json.loads(songs_ids):
            # TODO: sacar codigo repetido con app/songs
            song = pdb.query(SongModel).filter(SongModel.id == song_id).first()

            songs.append(song)
        playlist.songs = songs

    pdb.commit()
    return {"id": playlist_id}


@router.delete("/playlists/{playlist_id}")
def delete_playlist(
    uid: str,
    playlist_id: str,
    pdb: Session = Depends(get_db),
):
    """Deletes a playlist by its id"""
    playlist = pdb.query(PlaylistModel).filter(PlaylistModel.id == playlist_id).first()
    if playlist is None:
        raise HTTPException(
            status_code=404, detail=f"Playlist '{playlist_id}' not found"
        )

    if uid != playlist.creator_id:
        raise HTTPException(
            status_code=403,
            detail=f"User '{uid} attempted to delete playlist of user with ID {playlist.creator_id}",
        )
    pdb.query(PlaylistModel).filter(PlaylistModel.id == playlist_id).delete()
    pdb.commit()