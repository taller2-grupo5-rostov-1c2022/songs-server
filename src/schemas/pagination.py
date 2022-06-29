from __future__ import annotations
from pydantic.generics import GenericModel
from typing import List, Optional, Union
from typing import TypeVar, Generic

T = TypeVar("T")


class CustomPage(GenericModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: Optional[Union[int, str]] = None

    def __init__(self, items: List[T], total: int, limit: int, offset: int):
        super().__init__(items=items, total=total, limit=limit, offset=offset)

    def __iter__(self):
        return self.items.__iter__()
