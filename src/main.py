from fastapi import (
    FastAPI,
    Depends,
)
from src.app import songs, albums, users, playlists
from src.middleware.utils import get_api_key

API_VERSION_PREFIX = "/api/v3"

app = FastAPI(
    title="Songs API",
    description="Spotifiuby's API to manage songs, albums, playlists and users",
    version="3.4.0",
    dependencies=[Depends(get_api_key)],
)

app.include_router(songs.router, prefix=API_VERSION_PREFIX)
app.include_router(albums.router, prefix=API_VERSION_PREFIX)
app.include_router(users.router, prefix=API_VERSION_PREFIX)
app.include_router(playlists.router, prefix=API_VERSION_PREFIX)
