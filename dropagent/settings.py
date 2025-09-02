# dropagent/settings.py
from pathlib import Path
import os
import dj_database_url  # pip install dj-database-url psycopg2-binary whitenoise

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------
# Security
# --------------------------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-but-hardcoded")
DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1"]

CSRF_TRUSTED_ORIGINS = [
    "https://*.up.railway.app",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# --------------------------------------------------------------------
# Installed apps
# --------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # local apps
    "core",
    "users",
    "parcels",
    "shops",
    "earnings",
    "notifications",
    "riders",
    "dashboard",
    "widget_tweaks",
]

# --------------------------------------------------------------------
# Middleware
# --------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serve static on Railway
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "dropagent.urls"

# --------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dropagent.wsgi.application"

# --------------------------------------------------------------------
# Database
# --------------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=True,  # force SSL for Railway Postgres
    )
}

# Extra fallback for some psycopg2 versions
if DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
    DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}

# --------------------------------------------------------------------
# Custom User Model
# --------------------------------------------------------------------
AUTH_USER_MODEL = "users.User"

# --------------------------------------------------------------------
# Password Validators
# --------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
]

# --------------------------------------------------------------------
# i18n
# --------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------
# Static & Media
# --------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --------------------------------------------------------------------
# Auth Redirects
# --------------------------------------------------------------------
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

# --------------------------------------------------------------------
# Twilio (optional)
# --------------------------------------------------------------------
TWILIO_FROM = os.getenv("TWILIO_FROM", "")
