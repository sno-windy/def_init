from pathlib import Path
from .base import *

DEBUG = True

ALLOWED_HOSTS = "*"

INSTALLED_APPS += ["debug_toolbar"]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# debug_toolbar
INTERNAL_IPS = ['127.0.0.1', '192.168.33.1']
