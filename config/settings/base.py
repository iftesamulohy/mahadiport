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
    # Both must precede django.contrib.admin (template + admin overrides).
    "django_bangla_admin",
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
    # Returns only the content region for the admin's HTMX (SPA) navigation.
    # Pages without its markers (the public site's HTMX partials) pass through.
    "django_bangla_admin.middleware.HtmxShellMiddleware",
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
                "django_bangla_admin.context_processors.bangla_admin",
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


# django-bangla-admin — themed admin + dashboard (see README "Admin").
# Note: its EN/বাং toggle sets the same django_language cookie as the public
# site, so switching the admin language also switches the site for that browser.
BANGLA_ADMIN = {
    "site_title": "Mahadi Admin",
    "site_header": "Mahadi Admin",
    "site_brand": {"bn": "মাহাদি অ্যাডমিন", "en": "Mahadi Admin"},
    "welcome_sign": {"bn": "স্বাগতম, মাহাদি", "en": "Welcome back, Mahadi"},
    "copyright": "mdmahadihasan.com",
    "theme": "dark",
    "primary_color": "#4D8DFF",  # matches the site's dark-mode accent
    "default_language": "en",
    "menu": [
        {"label": {"bn": "ড্যাশবোর্ড", "en": "Dashboard"},
         "icon": "layout-dashboard", "url": "bangla_admin:index"},
        {"section": {"bn": "লিড", "en": "Leads"}},
        {"label": {"bn": "লিড", "en": "Leads"}, "icon": "bell", "model": "leads.Lead"},
        {"section": {"bn": "পোর্টফোলিও", "en": "Portfolio"}},
        {"label": {"bn": "কেস স্টাডি", "en": "Case studies"},
         "icon": "folder", "model": "portfolio.CaseStudy"},
        {"label": {"bn": "স্ট্যাট কাউন্টার", "en": "Stat counters"},
         "icon": "trending-up", "model": "portfolio.StatCounter"},
        {"label": {"bn": "অভিজ্ঞতা", "en": "Experience"},
         "icon": "activity", "model": "portfolio.Experience"},
        {"label": {"bn": "স্কিল ক্যাটাগরি", "en": "Skill categories"},
         "icon": "tag", "model": "portfolio.SkillCategory"},
        {"label": {"bn": "স্কিল", "en": "Skills"}, "icon": "package", "model": "portfolio.Skill"},
        {"label": {"bn": "টেস্টিমোনিয়াল", "en": "Testimonials"},
         "icon": "users", "model": "portfolio.Testimonial"},
        {"section": {"bn": "সেটিংস", "en": "Settings"}},
        {"label": {"bn": "সাইট সেটিংস", "en": "Site settings"},
         "icon": "settings", "model": "core.SiteSettings"},
        {"label": {"bn": "ইউজার", "en": "Users"}, "icon": "user", "model": "auth.User"},
        {"label": {"bn": "গ্রুপ", "en": "Groups"}, "icon": "shield", "model": "auth.Group"},
    ],
    "stat_cards": [
        {"label": {"bn": "মোট লিড", "en": "Total leads"},
         "model": "leads.Lead", "aggregate": "count", "icon": "users"},
        {"label": {"bn": "অপঠিত লিড", "en": "Unread leads"},
         "model": "leads.Lead", "aggregate": "count",
         "filters": {"is_read": False}, "icon": "bell"},
        {"label": {"bn": "কেস স্টাডি", "en": "Case studies"},
         "model": "portfolio.CaseStudy", "aggregate": "count", "icon": "folder"},
        {"label": {"bn": "প্রুফ স্ক্রিনশট", "en": "Proof screenshots"},
         "model": "portfolio.CaseStudyScreenshot", "aggregate": "count", "icon": "activity"},
    ],
    "charts": [
        {"id": "leads_by_month", "kind": "line", "size": "ba-col-12",
         "title": {"bn": "মাসিক লিড", "en": "Leads per month"},
         "model": "leads.Lead", "group_by": "created_at", "trunc": "month",
         "aggregate": "count", "limit": 12},
        {"id": "leads_by_budget", "kind": "doughnut",
         "title": {"bn": "বাজেট অনুযায়ী লিড", "en": "Leads by monthly budget"},
         "model": "leads.Lead", "group_by": "monthly_budget", "aggregate": "count"},
        {"id": "screenshots_per_case", "kind": "bar",
         "title": {"bn": "কেস অনুযায়ী স্ক্রিনশট", "en": "Screenshots per case"},
         "model": "portfolio.CaseStudyScreenshot", "group_by": "case_study__title_en",
         "aggregate": "count"},
        {"id": "screenshots_by_kind", "kind": "doughnut",
         "title": {"bn": "প্রুফের ধরন", "en": "Proof screenshots by type"},
         "model": "portfolio.CaseStudyScreenshot", "group_by": "kind", "aggregate": "count"},
        {"id": "skills_per_category", "kind": "bar",
         "title": {"bn": "ক্যাটাগরি অনুযায়ী স্কিল", "en": "Skills per category"},
         "model": "portfolio.Skill", "group_by": "category__name_en", "aggregate": "count"},
    ],
}


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
