"""
Django settings for bookbazaar_backend project.
Developed for BookBazaar - Pakistan's Used Books Marketplace
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
load_dotenv(BASE_DIR / '.env')

# Security Key
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-0hirqm$&uvt$6x=83#v3lf=03_sg=bm)gmpab&a5x_b2=oe3=n')

# Debug Mode
DEBUG = os.environ.get('DEBUG', 'True').strip().lower() in ('true', '1', 'yes')

# Allowed Hosts
if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost')
    ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]
    if '.onrender.com' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('.onrender.com')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'bazaar',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bookbazaar_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bookbazaar_backend.wsgi.application'

# Database Configuration: Render DATABASE_URL support, PostgreSQL toggle, SQLite fallback
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = os.environ.get('USE_POSTGRES', 'False').strip().lower() in ('true', '1', 'yes')

if DATABASE_URL:
    from urllib.parse import urlparse
    parsed = urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed.path.lstrip('/'),
            'USER': parsed.username or '',
            'PASSWORD': parsed.password or '',
            'HOST': parsed.hostname or '',
            'PORT': str(parsed.port or 5432),
            'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '600')),
        }
    }
elif USE_POSTGRES:
    _pg_available = False
    try:
        import socket
        _s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _s.settimeout(0.5)
        _s.connect((os.environ.get('DB_HOST', '127.0.0.1'), int(os.environ.get('DB_PORT', '5432'))))
        _s.close()
        _pg_available = True
    except Exception:
        _pg_available = False

    if _pg_available:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('DB_NAME', 'bookbazaar_db'),
                'USER': os.environ.get('DB_USER', 'bookbazaar_user'),
                'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
                'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
                'PORT': os.environ.get('DB_PORT', '5432'),
                'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '600')),
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage" if not DEBUG else "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CORS Configuration
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    cors_env = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://127.0.0.1:8000,http://localhost:8000')
    CORS_ALLOWED_ORIGINS = [c.strip() for c in cors_env.split(',') if c.strip()]

# CSRF Trusted Origins for Form Submissions & API
csrf_trusted_env = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://127.0.0.1:8000,http://localhost:8000')
CSRF_TRUSTED_ORIGINS = [c.strip() for c in csrf_trusted_env.split(',') if c.strip()]
if 'https://*.onrender.com' not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append('https://*.onrender.com')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration with Throttling & Token Authentication
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': os.environ.get('THROTTLE_ANON_RATE', '60/min'),
        'user': os.environ.get('THROTTLE_USER_RATE', '200/min'),
    },
}

# Production Security Headers & Cookies
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

if not DEBUG:
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() in ('true', '1')
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1')
    CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False').lower() in ('true', '1')
    if SECURE_SSL_REDIRECT:
        SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '31536000'))
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Logging Configuration
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'bookbazaar.log',
            'encoding': 'utf-8',
            'formatter': 'standard',
            'mode': 'a',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'bazaar': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# ==========================================
# Payment Gateway Configuration (Phase 3)
# ==========================================
# Gateway Mode: 'sandbox' (default, safe for testing) or 'live'
PAYMENT_GATEWAY_MODE = os.environ.get('PAYMENT_GATEWAY_MODE', 'sandbox').strip().lower()

# JazzCash Merchant Credentials (from Mobilink Microfinance Bank)
JAZZCASH_MERCHANT_ID = os.environ.get('JAZZCASH_MERCHANT_ID', '').strip()
JAZZCASH_PASSWORD = os.environ.get('JAZZCASH_PASSWORD', '').strip()
JAZZCASH_INTEGRITY_SALT = os.environ.get('JAZZCASH_INTEGRITY_SALT', '').strip()
JAZZCASH_RETURN_URL = os.environ.get('JAZZCASH_RETURN_URL', 'http://127.0.0.1:8000/api/payments/jazzcash/callback/').strip()
JAZZCASH_API_URL = os.environ.get(
    'JAZZCASH_API_URL',
    'https://sandbox.jazzcash.com.pk/CustomerPortal/transactionmanagement/merchantform/' if PAYMENT_GATEWAY_MODE == 'sandbox'
    else 'https://payments.jazzcash.com.pk/CustomerPortal/transactionmanagement/merchantform/'
).strip()

# Easypaisa Merchant Credentials (from Telenor Microfinance Bank)
EASYPAISA_STORE_ID = os.environ.get('EASYPAISA_STORE_ID', '').strip()
EASYPAISA_HASH_KEY = os.environ.get('EASYPAISA_HASH_KEY', '').strip()
EASYPAISA_RETURN_URL = os.environ.get('EASYPAISA_RETURN_URL', 'http://127.0.0.1:8000/api/payments/easypaisa/callback/').strip()
EASYPAISA_API_URL = os.environ.get(
    'EASYPAISA_API_URL',
    'https://easypaystg.easypaisa.com.pk/easypay/Index.jsf' if PAYMENT_GATEWAY_MODE == 'sandbox'
    else 'https://easypay.easypaisa.com.pk/easypay/Index.jsf'
).strip()
