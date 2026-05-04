"""Ajustes comodos para trabajar en local o dentro de Docker."""
from .base import *

DEBUG = True

# En local se deja abierto para entrar desde localhost, Docker o la IP de la maquina.
ALLOWED_HOSTS = ['*']

# Logs en consola. Las queries ayudan bastante cuando se revisan filtros y listados.
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
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
