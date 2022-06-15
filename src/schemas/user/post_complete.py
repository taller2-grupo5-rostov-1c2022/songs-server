from typing import Optional, Any
from pydantic.utils import GetterDict
from datetime import datetime
from .post import UserPost


class UserGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        if key == "uid":
            return self._obj.attrib.get("id", default)
        else:
            try:
                return self._obj.find(key).attrib['Value']
            except (AttributeError, KeyError):
                return default


class UserPostComplete(UserPost):
    wallet: str
    sub_level: int
    sub_expires: Optional[datetime]

    class Config:
        getter_dict = UserGetter
