from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    position = models.CharField(max_length=20)
    like_count = models.PositiveIntegerField(default=0) #?
    user_image = models.ImageField(upload_to="image/", default="default.png") #defaultを仮で入れた。

class Article(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_article")
    title = models.CharField(max_length=30)
    content = models.TextField()
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

class Question(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_question")
    title = models.CharField(max_length=30)
    content = models.TextField()
    if_answered = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now) #不要説　

class Task(models.Model):
    title = models.CharField(max_length=30)
    clear = models.BooleanField(default=False)

class Talk(models.Model):
    msg = models.CharField(max_length=120)
    msg_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_form")
    msg_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_to")
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}から{}へのメッセージ".format(self.msg_from,self.msg_to)

#add
class TalkAtArticle(Talk):
    msg_at = models.ForeignKey(Article, on_delete=models.CASCADE)

class TalkAtQuestion(Talk):
    msg_at = models.ForeignKey(Question, on_delete=models.CASCADE)
