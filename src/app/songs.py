import datetime

from src import roles, utils, schemas
from src.constants import STORAGE_PATH, SUPPRESS_BLOB_ERRORS
from typing import List
from fastapi import APIRouter
from fastapi import Depends, File, HTTPException, UploadFile
from src.firebase.access import get_bucket
from sqlalchemy.orm import Session
from src.database.access import get_db
from src.database import models
from src.roles import get_role

router = APIRouter(tags=["songs"])


def create_song_artists_models(artists_names: List[str]):
    artists = []
    for artist_name in artists_names:
        artists.append(models.ArtistModel(name=artist_name))
    return artists


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

    return utils.song.get_songs(pdb, role, creator, artist, genre, sub_level, name)


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

    song_update = song_update.dict()

    for song_attr in song_update:
        if song_update[song_attr] is not None:
            setattr(song, song_attr, song_update[song_attr])
    if song_update["artists_names"] is not None:
        song.artists = create_song_artists_models(song_update["artists_names"])

    if song_update["blocked"] is not None:
        if not role.can_block():
            raise HTTPException(
                status_code=403,
                detail=f"User {uid} without permissions tried to block song {song.id}",
            )
        song.blocked = song_update["blocked"]

    if file is not None:
        try:
            blob = bucket.blob(f"songs/{song.id}")
            blob.upload_from_file(file.file)
            blob.make_public()
            song.file_last_update = datetime.datetime.now()
        except:  # noqa: W0707 # Want to catch all exceptions
            if not SUPPRESS_BLOB_ERRORS:
                raise HTTPException(
                    status_code=507, detail=f"Files for Song '{song.id}' not found"
                )

    pdb.commit()


@router.post("/songs/", response_model=schemas.SongBase)
def post_song(
    song_info: schemas.SongPost = Depends(utils.album.retrieve_song),
    file: UploadFile = File(...),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Creates a song and returns its id. Artists form is encoded like '["artist1", "artist2", ...]'"""

    new_song = models.SongModel(
        **song_info.dict(exclude={"artists_names"}),
        artists=create_song_artists_models(song_info.artists_names),
        file_last_update=datetime.datetime.now(),
    )
    pdb.add(new_song)
    pdb.commit()

    try:
        blob = bucket.blob(f"songs/{new_song.id}")
        blob.upload_from_file(file.file)
        blob.make_public()
    except:  # noqa: W0707 # Want to catch all exceptions
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507,
                detail=f"Could not upload Files for new Song {new_song.id}",
            )

    # Changes to the db should not be committed if there is an error
    # uploading the file
    pdb.add(new_song)
    pdb.commit()

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

    if uid != song.creator_id and not role.can_delete_everything():
        raise HTTPException(
            status_code=403,
            detail=f"User with ID {uid} attempted to delete song of creator with ID {song.creator_id}",
        )

    pdb.delete(song)

    try:
        bucket.blob(f"songs/{song.id}").delete()
    except:  # noqa: W0707 # Want to catch all exceptions
        if not SUPPRESS_BLOB_ERRORS:
            raise HTTPException(
                status_code=507, detail=f"Could not delete Song {song.id}"
            )

    pdb.commit()


@router.get("/my_songs/", response_model=List[schemas.SongBase])
def get_my_songs(
    uid: str = Depends(utils.user.retrieve_uid), pdb: Session = Depends(get_db)
):
    return utils.song.get_songs(pdb, roles.Role.admin(), uid)
