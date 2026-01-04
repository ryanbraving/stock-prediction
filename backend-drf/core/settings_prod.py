import os
from .settings import *

# Production settings for Lambda
DEBUG = False
ALLOWED_HOSTS = ['*']  # Lambda handles routing

# Use environment variables for production
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database - Use RDS in production
if os.environ.get('RDS_ENDPOINT'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('RDS_DB_NAME'),
            'USER': os.environ.get('RDS_USERNAME'),
            'PASSWORD': os.environ.get('RDS_PASSWORD'),
            'HOST': os.environ.get('RDS_ENDPOINT'),
            'PORT': os.environ.get('RDS_PORT', '5432'),
        }
    }

# Static files for Lambda
STATIC_URL = '/static/'
STATIC_ROOT = '/tmp/static/'

# Media files - Use S3 in production
MEDIA_URL = '/media/'
MEDIA_ROOT = '/tmp/media/'

# CORS for production
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
    "http://localhost:5173",  # Keep for development
]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}