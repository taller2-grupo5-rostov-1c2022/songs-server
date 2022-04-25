from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config
import os

# SQLALCHEMY_DATABASE_URL = f"{dialect}://{username}:{password}@{host}:{port}/{database}"


if os.environ.get("TESTING") == "1":
    print("TEST DB")
    POSTGRES_URL = config(
        "TEST_POSTGRES_URL", default="postgresql://test:test@localhost:5438/test"
    )

    engine = create_engine(POSTGRES_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = declarative_base()

    def get_db():
        try:
            db = SessionLocal()
            yield db
        finally:
            db.close()

else:
    print("REAL DB")
    POSTGRES_URL = config("POSTGRES_URL", default="")

    engine = create_engine(POSTGRES_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = declarative_base()

    def get_db():
        db = SessionLocal()
        try:
            yield db
        except:  # noqa: E722 # Want to catch all exceptions
            db.close()
