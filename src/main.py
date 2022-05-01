from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Security,
    Request,
)
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from src.postgres import models
from src.app import songs, albums, users
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.postgres.database import Base
from src.mocks.firebase.bucket import bucket_mock
from src.firebase.access import get_bucket
from src.postgres.database import get_db

import os

API_KEY = os.environ.get("API_KEY") or "key"
API_KEY_NAME = "api_key"


async def get_api_key(
    api_key_header: str = Security(APIKeyHeader(name=API_KEY_NAME, auto_error=True)),
):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403)


app = FastAPI(dependencies=[Depends(get_api_key)])

if os.environ.get("TESTING") == "1":
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


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = str("*")
    return response


###### IMPORTANTE: SACAR ESTA LINEA AL HACER EL DEPLOY ##############
if os.environ.get("TESTING") == "1":
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    app.include_router(songs.router, prefix="/api/v3")
    app.include_router(albums.router, prefix="/api/v3")
    app.include_router(users.router, prefix="/api/v3")
