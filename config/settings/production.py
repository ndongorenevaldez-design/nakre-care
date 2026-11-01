from .base import *

if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured(
        "Provide a strong DJANGO_SECRET_KEY (at least 50 characters)."
    )
if not ALLOWED_HOSTS or any("*" in h or h.startswith(".") for h in ALLOWED_HOSTS):
    raise ImproperlyConfigured("Explicit DJANGO_ALLOWED_HOSTS required.")
if not os.environ.get("DATABASE_URL"):
    raise ImproperlyConfigured("Private PostgreSQL DATABASE_URL required.")
origin = urlsplit(PUBLIC_ORIGIN)
if (
    origin.scheme != "https"
    or origin.netloc not in ALLOWED_HOSTS
    or origin.path
    or origin.query
    or origin.fragment
):
    raise ImproperlyConfigured("PUBLIC_ORIGIN must be an exact allowed HTTPS origin.")
CSRF_TRUSTED_ORIGINS = [PUBLIC_ORIGIN]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600
# Enable only after Railway's header replacement behavior has been verified.
if os.environ.get("TRUST_PROXY_HTTPS") == "1":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
