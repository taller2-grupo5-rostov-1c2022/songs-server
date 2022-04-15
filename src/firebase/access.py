import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage

from dotenv import load_dotenv

load_dotenv()

# Use a service account

cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "rostov-spotifiuby",
    "private_key_id": os.environ.get("FIREBASE_ID"),
    "private_key": os.environ.get("FIREBASE_KEY"),
    "client_email": "firebase-adminsdk-1ec7p@rostov-spotifiuby.iam.gserviceaccount.com",
    "client_id": "108071383804591709093",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-1ec7p%40rostov"
    "-spotifiuby.iam.gserviceaccount.com "
})

firebase_admin.initialize_app(cred, {
    'storageBucket': 'rostov-spotifiuby.appspot.com/'
})

db = firestore.client()
bucket = storage.bucket("rostov-spotifiuby.appspot.com")
