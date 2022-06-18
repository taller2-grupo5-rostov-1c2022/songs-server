from pydantic import BaseModel


class UserPost(BaseModel):
    uid: str
    name: str
    location: str
    interests: str

    class Config:
        orm_mode = True

        example = {
            "uid": "123456789",
            "name": "John Doe",
            "location": "New York, NY",
            "interests": "Rock, Pop, Jazz",
        }
