from src.exceptions import MessageException
from typing import Optional
from fastapi import Form
import json


def retrieve_artists_names_update(artists: Optional[str] = Form(None)):
    if artists is not None:
        try:
            artists = json.loads(artists)
            if len(artists) == 0:
                raise MessageException(
                    status_code=422, detail="There must be at least one artist"
                )
        except ValueError as e:
            raise MessageException(
                status_code=422, detail="Artists string is not well encoded"
            ) from e
    return artists


def retrieve_artists_names(
    artists: str = Form(...),
):
    return retrieve_artists_names_update(artists=artists)
