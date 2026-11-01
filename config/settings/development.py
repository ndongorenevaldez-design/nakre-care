from .base import *
import secrets

# Ephemeral local key only: no production fallback and no predefined credential.
SECRET_KEY = SECRET_KEY or secrets.token_urlsafe(64)
DEBUG = True
ALLOWED_HOSTS = ALLOWED_HOSTS or ["localhost", "127.0.0.1", "testserver"]
STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
}
