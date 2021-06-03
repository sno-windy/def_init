from pathlib import Path
from .base import *

DEBUG = True

ALLOWED_HOSTS = "*"

INSTALLED_APPS += ["debug_toolbar"]

# STATICFILES_DIRS = (
#     str(Path(BASE_DIR) / 'static'),
# )

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# debug_toolbar
INTERNAL_IPS = ['127.0.0.1', '192.168.33.1']
