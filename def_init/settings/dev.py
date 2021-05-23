from pathlib import Path
from .base import *

DEBUG = True

ALLOWED_HOSTS = "*"

INSTALLED_APPS += ["debug_toolbar"]

STATICFILES_DIRS = (
    str(Path(BASE_DIR) / 'static'),
)
# STATIC_ROOT = BASE_DIR / 'static'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
