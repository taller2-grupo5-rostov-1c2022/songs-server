import os

ENVIRONTMENT = str(os.environ.get("ENVIRONMENT", "dev"))
API_KEY = os.environ.get("API_KEY", "key")
API_KEY_NAME = "api_key"
PAYMENTS_API_KEY = os.environ.get("PAYMENTS_API_KEY", "key")
TESTING = int(os.environ.get("TESTING", False))
SUPPRESS_BLOB_ERRORS = False
STORAGE_PATH = "https://storage.googleapis.com/rostov-spotifiuby.appspot.com/"
AGORA_APP_ID = os.environ.get("AGORA_APP_ID", "")
AGORA_APP_CERT = os.environ.get("AGORA_APP_CERT", "")
