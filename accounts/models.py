from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    position = models.CharField(max_length=20)
    like_count = models.PositiveIntegerField(default=0)
    user_image = models.ImageField(upload_to="image/", default="default.png")
