from django.db import models
from django.contrib.auth.models import AbstractUser
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill

class User(AbstractUser):
    username = models.CharField(max_length=8)
    position = models.CharField(max_length=15)
    like_count = models.PositiveIntegerField(default=0)
    user_image = ProcessedImageField(upload_to="accounts/img",
        processors=[ResizeToFill(250,250)],
        format='JPEG',
        options={'quality':60})