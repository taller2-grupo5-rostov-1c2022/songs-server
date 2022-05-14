import firebase_admin
import json
from src.constants import TESTING
from firebase_admin import credentials, storage, auth
from src.mocks.firebase.bucket import bucket_mock
from src.mocks.firebase.auth import auth_mock

from dotenv import load_dotenv

load_dotenv()

bucket = bucket_mock
_auth = auth_mock

if not TESTING:
    # Use a service account
    # Si tira error porque no encuentra el archivo, copiar el google-credentials.json a /src
    with open("google-credentials.json") as json_file:
        cert_dict = json.load(json_file, strict=False)

    cred = credentials.Certificate(cert_dict)

    firebase_admin.initialize_app(
        cred, {"storageBucket": "rostov-spotifiuby.appspot.com/"}
    )

    bucket = storage.bucket("rostov-spotifiuby.appspot.com")

    _auth = auth


def get_bucket():
    return bucket


def get_auth():
    return _auth
