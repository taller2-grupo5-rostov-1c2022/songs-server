from fastapi import FastAPI, Depends, Request
from src.app import (
    songs,
    albums,
    users,
    playlists,
    favorites,
    reviews,
    comments,
    streamings,
    subscriptions,
)
from src.exceptions import MessageException
from src.middleware.utils import get_api_key
from fastapi.responses import JSONResponse

API_VERSION_PREFIX = "/api/v3"

app = FastAPI(
    title="Songs API",
    description="Spotifiuby's API to manage songs, albums, playlists and users",
    version="3.6.0",
    dependencies=[Depends(get_api_key)],
)

app.include_router(songs.router, prefix=API_VERSION_PREFIX)
app.include_router(albums.router, prefix=API_VERSION_PREFIX)
app.include_router(users.router, prefix=API_VERSION_PREFIX)
app.include_router(playlists.router, prefix=API_VERSION_PREFIX)
app.include_router(favorites.router, prefix=API_VERSION_PREFIX)
app.include_router(reviews.router, prefix=API_VERSION_PREFIX)
app.include_router(comments.router, prefix=API_VERSION_PREFIX)
app.include_router(streamings.router, prefix=API_VERSION_PREFIX)
app.include_router(subscriptions.router, prefix=API_VERSION_PREFIX)


@app.exception_handler(MessageException)
async def message_exception_handler(_request: Request, exc: MessageException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message},
    )
