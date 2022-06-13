from pydantic import BaseModel


class SubLevelBase(BaseModel):
    sub_level: int
