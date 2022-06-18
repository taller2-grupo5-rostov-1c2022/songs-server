from pydantic import BaseModel


class UserBase(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True

        example = {
            "uid": "123456789",
            "name": "John Doe",
        }
