"""Ajustes pensados para desplegar la aplicacion sin DEBUG."""
from .base import *

DEBUG = False

# En produccion conviene poner aqui solo el dominio real desde la variable .env.

# Cabeceras basicas de seguridad para navegador.
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Activar cuando el servidor tenga HTTPS funcionando de verdad.
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000

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
        'level': 'WARNING',
    },
}
