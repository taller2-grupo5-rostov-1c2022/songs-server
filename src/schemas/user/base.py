from pydantic import BaseModel


class UserBase(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True
