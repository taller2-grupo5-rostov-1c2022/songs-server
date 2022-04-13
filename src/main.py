from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Song(BaseModel):
    name: str

song1 = Song(name = "song1")

song2 = Song(name = "song2")

songs = [song1, song2]

class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

@app.get("/api/v1/songs/")
def read_songs():
    """Devuelve todas las canciones de la db"""
    return songs

@app.get("/api/v1/songs/{song_id}")
def read_songs_id(song_id: int):
    """Devuelve una cancion segun su id, o 404 si no la encuentra"""
    if len(songs) <= song_id:
        raise HTTPException(status_code=404, detail="Song not found")
    return songs[song_id]

@app.post("/api/v1/songs/")
def post_song(song: Song):
    songs.append(song)
    return {"id": len(songs)-1}
