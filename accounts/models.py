from django.db import models
from django.contrib.auth.models import AbstractUser
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill

class User(AbstractUser):
    position = models.CharField(max_length=20)
    like_count = models.PositiveIntegerField(default=0)
    user_image = models.ImageField(upload_to="accounts/img", default="accounts/img/default.png")
    user_image_thumbnail = ImageSpecField(source='user_image',
    processors=[ResizeToFill(250,250)],
    format='JPEG',
    options={'quality':60})