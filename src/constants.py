import os

API_KEY = os.environ.get("API_KEY", "key")
API_KEY_NAME = "api_key"
TESTING = int(os.environ.get("TESTING", False))
