from pydantic import BaseModel
from pydantic.utils import GetterDict
from typing import Any, Optional
from .user.base import UserBase


class StreamingGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        if key == "token":
            return self._obj.listener_token

        else:
            try:
                return getattr(self._obj, key)
            except (AttributeError, KeyError):
                return default


class StreamingBase(BaseModel):
    artist: UserBase
    token: str
    name: str
    img_url: Optional[str]

    class Config:
        orm_mode = True
        getter_dict = StreamingGetter
