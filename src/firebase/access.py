import firebase_admin
import json
from src.constants import TESTING
from firebase_admin import credentials
from firebase_admin import storage

from dotenv import load_dotenv

load_dotenv()

# Use a service account
with open("google-credentials.json") as json_file:
    cert_dict = json.load(json_file, strict=False)

    cred = credentials.Certificate(cert_dict)

    firebase_admin.initialize_app(
        cred, {"storageBucket": "rostov-spotifiuby.appspot.com/"}
    )

    bucket = storage.bucket("rostov-spotifiuby.appspot.com")


def get_bucket():
    return bucket
