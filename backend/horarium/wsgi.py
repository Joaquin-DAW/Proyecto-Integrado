"""Entrada WSGI que usaria Gunicorn en un despliegue clasico."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarium.settings.development')
application = get_wsgi_application()
