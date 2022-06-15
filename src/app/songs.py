import datetime

from src import roles, utils, schemas
from src.constants import STORAGE_PATH, SUPPRESS_BLOB_ERRORS
from typing import List
from fastapi import APIRouter
from fastapi import Depends, File, HTTPException, UploadFile, status

from src.firebase.access import get_bucket
from sqlalchemy.orm import Session
from src.database.access import get_db
from src.database import models
from src.roles import get_role
from src.database import crud

router = APIRouter(tags=["songs"])


@router.get("/songs/", response_model=List[schemas.SongBase])
def get_songs(
    creator: str = None,
    role: roles.Role = Depends(get_role),
    artist: str = None,
    genre: str = None,
    sub_level: int = None,
    name: str = None,
    pdb: Session = Depends(get_db),
):
    """Returns all songs"""

    songs = crud.song.get_songs(
        pdb, role.can_see_blocked(), creator, artist, genre, sub_level, name
    )
    return songs


@router.get("/songs/{song_id}", response_model=schemas.SongGet)
def get_song_by_id(
    song: models.SongModel = Depends(utils.song.get_song),
):
    """Returns a song by its id or 404 if not found"""

    song.file = (
        STORAGE_PATH
        + "songs/"
        + str(song.id)
        + "?t="
        + str(int(datetime.datetime.timestamp(song.file_last_update)))
    )

    return song


@router.put("/songs/{song_id}")
def update_song(
    song: models.SongModel = Depends(utils.song.get_song),
    uid: str = Depends(utils.user.retrieve_uid),
    role: roles.Role = Depends(get_role),
    song_update: schemas.SongUpdate = Depends(utils.song.retrieve_song_update),
    file: UploadFile = None,
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Updates song by its id"""

    if song.creator_id != uid and not role.can_edit_everything():
        raise HTTPException(
            status_code=403,
            detail=f"User '{uid} attempted to edit song of user with ID {song.creator_id}",
        )

    try:
        crud.song.update_song(pdb, song, song_update, role.can_block())
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail=f"User {uid} without permissions tried to block song {song.id}",
        )

    if file is not None:
        try:
            blob = bucket.blob(f"songs/{song.id}")
            blob.upload_from_file(file.file)
            blob.make_public()
            song_update = schemas.SongUpdateFile(
                file_last_update=datetime.datetime.now()
            )
            crud.song.update_song(pdb, song, song_update, role.can_block())
        except:  # noqa: W0707 # Want to catch all exceptions
            if not SUPPRESS_BLOB_ERRORS:
                raise HTTPException(
                    status_code=507, detail=f"Files for Song '{song.id}' not found"
                )


@router.post("/songs/", response_model=schemas.SongBase)
def post_song(
    song_post: schemas.SongPost = Depends(utils.album.retrieve_song),
    file: UploadFile = File(...),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Creates a song and returns its id. Artists form is encoded like '["artist1", "artist2", ...]'"""

    new_song = crud.song.create_song(pdb, song_post)

    try:
        blob = bucket.blob(f"songs/{new_song.id}")
        blob.upload_from_file(file.file)
        blob.make_public()
    except:  # noqa: W0707 # Want to catch all exceptions
        # Changes to the db should not be committed if there is an error
        # uploading the file
        crud.song.delete_song(pdb, new_song)
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507,
                detail=f"Could not upload Files for new Song {new_song.id}",
            )

    return new_song


@router.delete("/songs/{song_id}")
def delete_song(
    song: models.SongModel = Depends(utils.song.get_song),
    uid: str = Depends(utils.user.retrieve_uid),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
    role: roles.Role = Depends(get_role),
):
    """Deletes a song by its id"""

    if song.creator_id != uid and not role.can_delete_everything():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User '{uid} attempted to delete song of user with ID {song.creator_id}",
        )

    try:
        bucket.blob(f"songs/{song.id}").delete()
    except:  # noqa: W0707 # Want to catch all exceptions
        crud.song.create_song(pdb, schemas.SongPost.from_orm(song))
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507, detail=f"Could not delete Song {song.id}"
            )

    crud.song.delete_song(pdb, song)


@router.get("/my_songs/", response_model=List[schemas.SongBase])
def get_my_songs(
    uid: str = Depends(utils.user.retrieve_uid), pdb: Session = Depends(get_db)
):
    return crud.song.get_songs(pdb, show_blocked_songs=True, creator_id=uid)
