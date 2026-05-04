"""Entrada ASGI, util si mas adelante se añaden WebSockets o tareas async."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horarium.settings.development')
application = get_asgi_application()
