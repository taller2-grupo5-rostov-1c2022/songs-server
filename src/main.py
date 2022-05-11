from fastapi import (
    FastAPI,
    Depends,
)
from src.app import songs, albums, users, playlists
from src.middleware.utils import get_api_key

app = FastAPI(dependencies=[Depends(get_api_key)])

app.include_router(songs.router, prefix="/api/v3")
app.include_router(albums.router, prefix="/api/v3")
app.include_router(users.router, prefix="/api/v3")
app.include_router(playlists.router, prefix="/api/v3")
