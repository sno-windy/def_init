from django.db import models
from django.contrib.auth.models import AbstractUser
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

POSITION_CHOICE = (
    ('インターン生', 'インターン生'),
    ('エンジニア', 'エンジニア'),
    ('デザイナー', 'デザイナー'),
    ('凄いエンジニア', '凄いエンジニア'),
    ('素晴らしいデザイナー', '素晴らしいデザイナー'),
    ('運営', '運営'),
)


class User(AbstractUser):
    username = models.CharField(max_length=8, unique=True)
    position = models.CharField(
        max_length=16, choices=POSITION_CHOICE, default='インターン生')
    like_count = models.PositiveIntegerField(default=0)
    user_image = ProcessedImageField(upload_to="accounts/img",
                                     processors=[ResizeToFill(250, 250)],
                                     format='JPEG',
                                     options={'quality': 60},
                                     blank=True
                                     )
