import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage

from dotenv import load_dotenv

load_dotenv()

# Use a service account
cred = credentials.Certificate("/google-credentials.json")

firebase_admin.initialize_app(cred, {
    'storageBucket': 'rostov-spotifiuby.appspot.com/'
})

db = firestore.client()
bucket = storage.bucket("rostov-spotifiuby.appspot.com")
