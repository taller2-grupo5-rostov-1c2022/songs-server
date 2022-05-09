import firebase_admin
import json
from src.constants import TESTING
from firebase_admin import credentials
from firebase_admin import storage

from dotenv import load_dotenv

load_dotenv()

if not TESTING:
    # Use a service account
    # Si tira error porque no encuentra el archivo, copiar el google-credentials.json a /src
    with open("/code/src/google-credentials.json") as json_file:
        cert_dict = json.load(json_file, strict=False)

    cred = credentials.Certificate(cert_dict)

    firebase_admin.initialize_app(
        cred, {"storageBucket": "rostov-spotifiuby.appspot.com/"}
    )

    bucket = storage.bucket("rostov-spotifiuby.appspot.com")


def get_bucket():
    return bucket
