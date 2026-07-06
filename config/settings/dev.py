"""Development settings."""

from .base import *  # noqa: F401,F403
from .base import env_bool

DEBUG = env_bool("DEBUG", True)

ALLOWED_HOSTS = ["*"]

# Print emails (lead notifications) to the console in dev.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INTERNAL_IPS = ["127.0.0.1"]
