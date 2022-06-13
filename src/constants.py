import os

API_KEY = os.environ.get("API_KEY", "key")
API_KEY_NAME = "api_key"
TESTING = int(os.environ.get("TESTING", False))
FAST = int(os.environ.get("FAST", False))
SUPPRESS_BLOB_ERRORS = False
STORAGE_PATH = "https://storage.googleapis.com/rostov-spotifiuby.appspot.com/"
AGORA_APP_ID = os.environ.get("AGORA_APP_ID", "")
AGORA_APP_CERT = os.environ.get("AGORA_APP_CERT", "")
