from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from taggit.managers import TaggableManager
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.shortcuts import resolve_url
import requests
User = get_user_model()


class Article(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_article")
    title = models.CharField(max_length=30)
    # content = models.TextField(null=True)
    content = MarkdownxField()
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    tags = TaggableManager(blank=True)
    def __str__(self):
        return self.title

    def formatted_markdown(self):
        return markdownify(self.content)

class Question(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_question")
    title = models.CharField(max_length=30)
    content = models.TextField(null=True)
    if_answered = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return str(self.title)+" by "+str(self.poster)

    def browser_push(self,request):
        data = {
            'app_id':'ea35df03-ba32-4c85-9f7e-383106fb1d24',
            'safari_web_id': "web.onesignal.auto.47a2f439-afd3-4bb7-8cdd-92cc4f5ee46c",
            'included_segments': ['All'],
            'contents': {'en': self.title},
            'headings': {'en': '新しい質問が投稿されました！質問に答えましょう．'},
            'url': resolve_url('question_feed_new'),
        }
        requests.post(
            "https://onesignal.com/api/v1/notifications",
            headers={'Authorization': 'Basic MWY3ZjM5M2EtMmU2Ny00YjRiLWFhYzgtZDYwMjQyZTQ5NzI1'},
            json=data,
        )


class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Task(models.Model):
    title = models.CharField(max_length=30)
    contents = models.TextField(max_length=1000)
    clear = models.BooleanField(default=False)
    def __str__(self):
        return str(self.title)


class Talk(models.Model):
    msg = models.TextField(max_length=1000)
    msg_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_form")
    msg_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_to")
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}から{}へのメッセージ".format(self.msg_from,self.msg_to)

#add
class TalkAtArticle(Talk):
    msg_at = models.ForeignKey(Article, on_delete=models.CASCADE)

    def __str__(self):
        return "FROM '{}' TO '{}' AT '{}'".format(self.msg_from,self.msg_to,self.msg_at)
class TalkAtQuestion(Talk):
    msg_at = models.ForeignKey(Question, on_delete=models.CASCADE)
    def __str__(self):
        return "FROM '{}' TO '{}' AT '{}'".format(self.msg_from,self.msg_to,self.msg_at)
