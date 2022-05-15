import os

API_KEY = os.environ.get("API_KEY", "key")
API_KEY_NAME = "api_key"
TESTING = int(os.environ.get("TESTING", False))
SUPPRESS_BLOB_ERRORS = True
STORAGE_PATH = "https://storage.googleapis.com/rostov-spotifiuby.appspot.com/"
