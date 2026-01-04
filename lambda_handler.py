import os
import django
from django.conf import settings
from django.core.wsgi import get_wsgi_application

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from mangum import Mangum
from django.core.management import execute_from_command_line

# Get Django WSGI application
application = get_wsgi_application()

# Create Mangum handler for Lambda
handler = Mangum(application, lifespan="off")

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    """
    return handler(event, context)