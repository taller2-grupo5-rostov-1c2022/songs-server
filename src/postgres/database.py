from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config
import time
import os

if os.environ.get("TESTING") == "1":
    print("TEST DB")
    POSTGRES_URL = config(
        "TEST_POSTGRES_URL", default="postgresql://test:test@localhost:5438/test"
    )

else:
    POSTGRES_URL = config("POSTGRES_URL", default="")

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
    except:  # noqa: E722 # Want to catch all exceptions
        db.close()
