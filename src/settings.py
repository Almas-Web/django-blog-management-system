from dotenv import load_dotenv
from datetime import timedelta
import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# SECURITY

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")


# APPLICATIONS

INSTALLED_APPS = [
    # Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party Apps
    'corsheaders',
    'django_filters',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',

    # Our Apps
    'account',
    'blog',
]


# MIDDLEWARE

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# SECURITY HEADERS

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Keep False during local HTTP development
SECURE_SSL_REDIRECT = False

# Secure cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Enable HSTS after HTTPS deployment
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# CORS

CORS_ALLOWED_ORIGINS = []


# URL / TEMPLATE / WSGI

ROOT_URLCONF = 'src.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'src.wsgi.application'


# DATABASE

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}


# PASSWORD VALIDATION

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'MinimumLengthValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'NumericPasswordValidator'
        ),
    },
]


# INTERNATIONALIZATION

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# STATIC FILES

STATIC_URL = 'static/'


# MEDIA FILES

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')


# DEFAULT PRIMARY KEY

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# EMAIL

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")


# REST FRAMEWORK

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    'DEFAULT_SCHEMA_CLASS': (
        'drf_spectacular.openapi.AutoSchema'
    ),

    # Pagination
    'DEFAULT_PAGINATION_CLASS': (
        'rest_framework.pagination.PageNumberPagination'
    ),
    'PAGE_SIZE': 5,
    'PAGE_SIZE_QUERY_PARAM': 'page_size',
    'MAX_PAGE_SIZE': 10,

    # Throttling
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],

    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/min',
        'user': '1000/min',
    },
}


# JWT CONFIGURATION

SIMPLE_JWT = {
    # Access token
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),

    # Refresh token
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),

    # Refresh token rotation
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

    # Login tracking
    'UPDATE_LAST_LOGIN': False,

    # Signing
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,

    # Authorization header
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# API DOCUMENTATION

SPECTACULAR_SETTINGS = {
    'TITLE': 'Django Blog Management API',
    'DESCRIPTION': 'Production-style Blog Management API',
    'VERSION': '1.0.0',
}


# CUSTOM USER MODEL

AUTH_USER_MODEL = 'account.CustomUser'