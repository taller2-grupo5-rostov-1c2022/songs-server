from pydantic import BaseModel


class CommentUpdate(BaseModel):
    text: str

    class Config:
        orm_mode = True
