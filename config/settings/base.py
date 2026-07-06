"""
Base settings shared across dev and prod.
Portfolio site for Md Mahadi Hasan — Django + HTMX + Alpine.js.
"""

from pathlib import Path

import dj_database_url
from dotenv import load_dotenv
import os

# config/settings/base.py -> config/settings -> config -> project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")


def env(key, default=None):
    return os.environ.get(key, default)


def env_bool(key, default=False):
    val = os.environ.get(key)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


SECRET_KEY = env(
    "SECRET_KEY",
    "django-insecure-#n6gnr^^*a=xo1hp)23#8f+xurp5g_(m#*2#9$im#+w=+mtmi-",
)

DEBUG = env_bool("DEBUG", True)

ALLOWED_HOSTS = [h.strip() for h in env("ALLOWED_HOSTS", "*").split(",") if h.strip()]


# Application definition

DJANGO_APPS = [
    # modeltranslation must precede django.contrib.admin.
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]

LOCAL_APPS = [
    "apps.core",
    "apps.portfolio",
    "apps.leads",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Force English on first visit (before Locale reads Accept-Language).
    "apps.core.middleware.DefaultEnglishMiddleware",
    # LocaleMiddleware sits after Session, before Common (language from cookie).
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "apps.core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database — SQLite in dev, DATABASE_URL (PostgreSQL) in prod.
DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
    )
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# English is the default (foreign clients); Bangla available via the switcher.
LANGUAGE_CODE = "en"
TIME_ZONE = "Asia/Dhaka"
USE_I18N = True
USE_TZ = True

from django.utils.translation import gettext_lazy as _  # noqa: E402

LANGUAGES = [
    ("en", _("English")),
    ("bn", _("বাংলা")),
]
LOCALE_PATHS = [BASE_DIR / "locale"]

# django-modeltranslation
MODELTRANSLATION_DEFAULT_LANGUAGE = "en"
MODELTRANSLATION_LANGUAGES = ("en", "bn")
MODELTRANSLATION_FALLBACK_LANGUAGES = ("en", "bn")


# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Lead notification recipient (Mahadi)
LEAD_NOTIFY_EMAIL = env("LEAD_NOTIFY_EMAIL", "mahadihasanshawons@gmail.com")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "no-reply@mahadihasan.com")
