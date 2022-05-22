from fastapi import HTTPException, Header, Depends

from src import roles
from src.postgres import models
from src.postgres.database import get_db


def retrieve_uid(uid: str = Header(...), pdb=Depends(get_db)):
    # The user is not in the database
    if pdb.get(models.UserModel, uid) is None:
        raise HTTPException(status_code=404, detail=f"User with ID {uid} not found")
    return uid


# Get favorite songs of user
# if not role.can_see_blocked(), return only non-blocked songs
# Use filter of pdb query to filter out blocked songs
def get_favorite_songs(pdb, uid: str, role: roles.Role):
    user = get_user(uid, pdb)
    if role.can_see_blocked():
        return user.favorite_songs
    else:
        pass

def get_user(uid: str, pdb=Depends(get_db)):
    user = pdb.get(models.UserModel, uid)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with ID {uid} not found")
    return user


def add_song_to_favorites(
    pdb, user: models.UserModel, song: models.SongModel, role: roles.Role
):

    if role.can_see_blocked():
        user.favorite_songs.append(song)
    elif song.blocked:
        raise HTTPException(status_code=403, detail="Song is blocked")
    else:
        user.favorite_songs.append(song)
    pdb.commit()


def remove_song_from_favorites(pdb, user: models.UserModel, song: models.SongModel):
    user.favorite_songs.remove(song)
    pdb.commit()
