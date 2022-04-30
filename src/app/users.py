from src.postgres import schemas
from typing import List
from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Depends, Security, UploadFile, File, Form
import json

from sqlalchemy.orm import Session
from src.postgres.database import get_db
from src.postgres.models import SongModel, ArtistSongModel, UserModel

import os

if os.environ.get("TESTING") == "1":
    print("RUNNING IN TESTING MODE: MOCKING ACTIVATED")
    from src.mocks.firebase.bucket import bucket
else:
    from src.firebase.access import bucket

router = APIRouter(tags=["users"])


@router.get("/users/", response_model=List[schemas.UserBase])
def get_all_users(pdb: Session = Depends(get_db)):
    """Returns all users"""
    users = pdb.query(UserModel).all()
    return users


@router.get("/users/{user_id}", response_model=schemas.UserBase)
def get_user_by_id(user_id: str, pdb: Session = Depends(get_db)):
    """Returns a user by its id or 404 if not found"""
    user = pdb.query(UserModel).filter_by(UserModel.id == user_id).first()
    return user


@router.post("/users/")
def post_user(user_id: str, user_name: str, pdb: Session = Depends(get_db)):
    """Creates a user and returns its id"""
    new_user = UserModel(id=user_id, name=user_name)
    pdb.add(new_user)
    pdb.commit()
    pdb.refresh(new_user)

    return {"user_id": user_id}


@router.delete("/users/")
def delete_user(user_id: str, pdb: Session = Depends(get_db)):
    """Deletes a user given its id or 404 if not found"""
    try:
        pdb.query(UserModel).filter_by(UserModel.id == user_id).delete()
        pdb.commit()

    except Exception as entry_not_found:
        raise HTTPException(
            status_code=404, detail=f"User '{user_id}' not found"
        ) from entry_not_found

    return {"user_id": user_id}


@router.post("/new_song/{song_id}")
def new_song(song_id: str, user_name: str, pdb: Session = Depends(get_db)):
    """Adds a song to the user's list of published songs and returns its username"""
    db_entry = db.collection("users").document(user_name).get()
    if not db_entry.exists:
        raise HTTPException(status_code=404, detail="User not found")

    user = db_entry.to_dict()
    user["songs"].append(song_id)
    db.collection("users").document(user_name).update(user)

    return {"user_name": user_name}


@router.delete("/delete_song/{song_id}")
def delete_song(user_name: str, song_id: str, pdb: Session = Depends(get_db)):
    """Deletes a song if the user is authorized.
    Returns the id of the song, 401 if not authorized, or 404 if the user or the song was not found"""

    r = requests.get(
        "https://rostov-song-server.herokuapp.com/songs/" + song_id,
        headers=headers,
    )
    song = r.json()

    artist_name = song["artist_name"]
    if artist_name != user_name:
        raise HTTPException(status_code=401, detail="User not authorized")

    db_entry = db.collection("users").document(artist_name).get()
    if not db_entry.exists:
        raise HTTPException(status_code=404, detail="User not found")

    r = requests.delete(
        "https://rostov-song-server.herokuapp.com/songs/?song_id=" + song_id,
        headers=headers,
    )
    print(r)
    user_dict = db_entry.to_dict()
    user_dict["songs"].remove(song_id)
    print(user_dict)
    db.collection("users").document(artist_name).update(user_dict)
    print("OK")

    return {"song_id": song_id}
