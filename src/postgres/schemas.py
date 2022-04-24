from pydantic import BaseModel


class CreateSongRequest(BaseModel):
    name: str
    artist_id: str
