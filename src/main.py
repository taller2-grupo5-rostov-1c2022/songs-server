from fastapi import (
    FastAPI,
    Depends,
)
from src.app import songs, albums, users, playlists
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.constants import TESTING
from src.middleware.utils import get_api_key
from src.postgres.database import Base
from src.mocks.firebase.bucket import bucket_mock
from src.firebase.access import get_bucket

from src.postgres.database import get_db

app = FastAPI(dependencies=[Depends(get_api_key)])

if TESTING:
    print("RUNNING IN TESTING MODE: MOCKING ACTIVATED")

    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db_mock = TestingSessionLocal()

    def override_get_db():
        try:
            yield db_mock
        finally:
            db_mock.close()

    def override_get_bucket():
        yield bucket_mock

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_bucket] = override_get_bucket

app.include_router(songs.router, prefix="/api/v3")
app.include_router(albums.router, prefix="/api/v3")
app.include_router(users.router, prefix="/api/v3")
app.include_router(playlists.router, prefix="/api/v3")
