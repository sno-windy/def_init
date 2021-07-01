from .base import *


DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1", "def-init.demia.co.jp"]

STATIC_ROOT = BASE_DIR / 'static'

SITE_ID = 4
# email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.muumuu-mail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
# secret_settings.pyにEMAIL_HOST_USERとEMAIL_HOST_PASSWORDとDEFAULT_FROM_EMAILを設定
# 登録済みのメールアドレスでないと送信できない

#AWS_S3
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
AWS_STORAGE_BUCKET_NAME = 'demia-def-init'
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"

ADMINS = [("Higaki", "souta0829win7@yahoo.co.jp")]

SESSION_COOKIE_SECURE = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/def-init/debug.log",  # パスは環境に合わせて、ファイルは作る
            "maxBytes": 1024 * 1024 * 512,
            "backupCount": 10,
            "formatter": "standard",
        },
        "console": {"level": "INFO", "class": "logging.StreamHandler", "formatter": "standard"},
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
            "filters": ["require_debug_false"],
        },
    },
    "loggers": {
        "django.security.DisallowedHost": {"handlers": ["null"], "propagate": False},
        "django": {"handlers": ["file", "console", "mail_admins"], "level": "DEBUG", "propagate": True,},  # NOQA: E231
        "main": {"handlers": ["file", "console", "mail_admins"], "level": "DEBUG", "propagate": True,},  # NOQA: E231
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': 'def-init.cjxtzhczhfg9.ap-northeast-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}
