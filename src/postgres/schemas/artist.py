from pydantic import BaseModel


class ArtistBase(BaseModel):
    name: str

    class Config:
        orm_mode = True
