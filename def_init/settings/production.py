from .base import *


DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "def-init.tk", "localhost"]

STATIC_ROOT = BASE_DIR / 'static'

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
