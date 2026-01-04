import os
import django
from django.conf import settings
from mangum import Mangum

# Configure Django settings for production
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_prod')
django.setup()

from django.core.wsgi import get_wsgi_application

# Create WSGI application
django_app = get_wsgi_application()

# Lambda handler using Mangum
handler = Mangum(django_app, lifespan="off")

def lambda_handler(event, context):
    return handler(event, context)