import firebase_admin
import json
from src.constants import TESTING, ENVIRONTMENT
from firebase_admin import credentials, storage, auth
from src.mocks.firebase.bucket import bucket_mock
from src.mocks.firebase.auth import auth_mock
from google.cloud.storage.bucket import Bucket

from dotenv import load_dotenv

load_dotenv()

bucket = bucket_mock
_auth = auth_mock


class BucketMuxDemux:
    def __int__(self, _bucket):
        self._bucket = _bucket

    def blob(
        self,
        blob_name,
        chunk_size=None,
        encryption_key=None,
        kms_key_name=None,
        generation=None,
    ):
        if ENVIRONTMENT == "dev":
            folder_name, file_name = blob_name.split("/")
            folder_name += "_dev"
            blob_name = f"{folder_name}/{file_name}"

        return self._bucket.blob(
            blob_name, chunk_size, encryption_key, kms_key_name, generation
        )

    def __getattr__(self, item):
        return getattr(self._bucket, item)


if not TESTING:
    # Use a service account
    # Si tira error porque no encuentra el archivo, copiar el google-credentials.json a /src
    with open("google-credentials.json") as json_file:
        cert_dict = json.load(json_file, strict=False)

    cred = credentials.Certificate(cert_dict)

    firebase_admin.initialize_app(
        cred, {"storageBucket": "rostov-spotifiuby.appspot.com/"}
    )

    real_bucket = storage.bucket("rostov-spotifiuby.appspot.com")
    bucket = BucketMuxDemux()
    bucket._bucket = real_bucket

    _auth = auth


def get_bucket():
    return bucket


def get_auth():
    return _auth
