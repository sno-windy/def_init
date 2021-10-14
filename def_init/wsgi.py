"""
WSGI config for def_init project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'def_init.settings.production')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'def_init.settings.dev')

application = get_wsgi_application()
