from src.postgres import schemas
from typing import List
from fastapi import APIRouter, Header
from fastapi import Depends, File, Form, HTTPException, UploadFile
import json
from src.crud import songs as crud_songs
from src.firebase.access import get_bucket
from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres.models import SongModel, ArtistSongModel, UserModel

router = APIRouter(tags=["songs"])


@router.get("/songs/", response_model=List[schemas.SongBase])
def get_songs(
    creator: str = None,
    pdb: Session = Depends(get_db),
):
    """Returns all songs"""

    return crud_songs.get_songs(pdb, creator)


@router.get("/songs/{song_id}")
def get_song_by_id(
    song_id: int, pdb: Session = Depends(get_db), bucket=Depends(get_bucket)
):
    """Returns a song by its id or 404 if not found"""
    song = crud_songs.get_song_by_id(pdb, song_id).__dict__

    blob = bucket.blob("songs/" + str(song_id))
    blob.make_public()

    song["file"] = blob.public_url
    return song


@router.put("/songs/{song_id}")
def update_song(
    song_id: str,
    uid: str = Form(...),
    name: str = Form(None),
    description: str = Form(None),
    artists: str = Form(None),
    file: UploadFile = None,
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Updates song by its id"""

    # even though id is an integer, we can compare with a string
    song = pdb.query(SongModel).filter(SongModel.id == song_id).first()
    if song is None:
        raise HTTPException(status_code=404, detail=f"Song '{song_id}' not found")
    if song.creator_id != uid:
        raise HTTPException(
            status_code=403,
            detail=f"User '{uid} attempted to edit song of user with ID {song.creator_id}",
        )

    if name is not None:
        song.name = name
    if description is not None:
        song.description = description
    if artists is not None:
        artists_list = []
        for artist_name in json.loads(artists):
            artists_list.append(ArtistSongModel(artist_name=artist_name))
        song.artists = artists_list

    pdb.commit()

    if file is not None:
        try:
            blob = bucket.blob("songs/" + song_id)
            blob.upload_from_file(file.file)
        except Exception as entry_not_found:
            raise HTTPException(
                status_code=404, detail=f"Files for Song '{song_id}' not found"
            ) from entry_not_found

    return schemas.SongResponse(success=True, id=song.id if song else song_id)


@router.post("/songs/")
def post_song(
    uid: str = Form(...),
    name: str = Form(...),
    description: str = Form(...),
    artists: str = Form(...),
    genre: str = Form(...),
    file: UploadFile = File(...),
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Creates a song and returns its id. Artists form is encoded like '["artist1", "artist2", ...]'"""

    # The user is not in the database
    if not pdb.query(UserModel).filter(UserModel.id == uid).all():
        raise HTTPException(status_code=403, detail=f"User with ID {uid} not found")

    parsed_artists = json.loads(artists)
    artists_models = []
    for artist_name in parsed_artists:
        artists_models.append(ArtistSongModel(artist_name=artist_name))

    new_song = SongModel(
        name=name,
        description=description,
        creator_id=uid,
        artists=artists_models,
        genre=genre,
    )
    pdb.add(new_song)
    pdb.commit()
    pdb.refresh(new_song)

    blob = bucket.blob(f"songs/{new_song.id}")
    blob.upload_from_file(file)
    blob.make_public()

    return schemas.SongResponse(success=True, id=new_song.id, file=blob.public_url)


@router.delete("/songs/{song_id}")
def delete_song(
    uid: str,
    song_id: str,
    pdb: Session = Depends(get_db),
    bucket=Depends(get_bucket),
):
    """Deletes a song by its id"""

    song = pdb.query(SongModel).filter(SongModel.id == song_id).first()
    if song is None:
        raise HTTPException(status_code=404, detail=f"Song '{song_id}' not found")

    if uid != song.creator_id:
        raise HTTPException(
            status_code=403,
            detail=f"User with ID {uid} attempted to delete song of creator with ID {song.creator_id}",
        )

    pdb.query(SongModel).filter(SongModel.id == song_id).delete()
    pdb.commit()
    blob = bucket.blob("songs/" + song_id)
    blob.delete()

    return {"song_id": song_id}


@router.get("/my_songs/")
def get_my_songs(uid: str = Header(...), pdb: Session = Depends(get_db)):
    return crud_songs.get_songs(pdb, uid)
