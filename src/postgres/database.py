import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time

from src.constants import TESTING
from dotenv import load_dotenv

load_dotenv()

if TESTING:
    print("TEST DB")
    POSTGRES_URL = os.environ.get(
        "TEST_POSTGRES_URL", "postgresql://test:test@test:5438/test"
    )
else:
    print("PROD DB")
    POSTGRES_URL = os.environ.get("POSTGRES_URL", "")

engine = create_engine(POSTGRES_URL)

for x in range(10):
    try:
        print("Trying to connect to DB - " + str(x))
        engine.connect()
        break
    except:  # noqa: E722 # Want to catch all exceptions
        time.sleep(1)
        engine = create_engine(POSTGRES_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.close()
        raise e
    finally:
        db.close()
