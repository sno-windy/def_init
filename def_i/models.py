from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    position = models.CharField(max_length=20)
    like_count = models.PositiveIntegerField(default=0)
    user_image = models.ImageField(upload_to="image/")

class Article(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_article")
    title = models.CharField(max_length=30)
    content = models.TextField()
    like_count = models.PositiveIntegerField(default=0)
    time = models.DateTimeField(default=timezone.now)

class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_question")
    title = models.CharField(max_length=30)
    content = models.TextField()
    solved = models.BooleanField(default=False)
    time = models.DateTimeField(default=timezone.now)

class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now)

class Kadai(models.Model):
    name = models.CharField()
    clear = models.BooleanField(default=False)

class Talk(models.Model):
    msg = models.CharField(max_length=120)
    msg_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_form")
    msg_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_to")
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}から{}へのメッセージ".format(self.msg_from,self.msg_to)









