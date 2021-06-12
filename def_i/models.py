import requests

from django.contrib.auth import get_user_model
from django.core.validators import validate_image_file_extension
from django.db import models
from django.db.models import Q
from django.shortcuts import resolve_url
from django.utils import timezone
from linebot import LineBotApi
from linebot.models import TextSendMessage
from markdownx.models import MarkdownxField
from .markdown import markdownify
from taggit.managers import TaggableManager
from stdimage.models import StdImageField

from def_init.secret_settings import *


User = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=10)
    category_image = models.FileField(upload_to='def_i/img')
    description = models.TextField(max_length=100, null=True)

    def __str__(self):
        return str(self.title)

class Course(models.Model):
    title = models.CharField(max_length=30)
    course_num = models.PositiveSmallIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"({self.category}-{self.course_num}){self.title}"


class Lesson(models.Model):
    title = models.CharField(max_length=30)
    contents = MarkdownxField(max_length=100000,null=True)
    lesson_num = models.PositiveSmallIntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="lessons")

    def __str__(self):
        return f"({self.course.category}-{self.course.course_num}-{self.lesson_num}){self.title}"

    def formatted_markdown(self):
        return markdownify(self.contents)


class ClearedLesson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "cleared_user")
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, related_name = "cleared_lesson", null=True)
    cleared_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} cleared lesson {self.lesson}"


class StudyingCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_category")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="studying_category")

    def __str__(self):
        return f"{self.user} now studying {self.category}"


class Article(models.Model):
    poster = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="user_article",null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="category_article", null=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, related_name="course_article", null=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, related_name="lesson_article", null=True)
    title = models.CharField(max_length=30)
    content = MarkdownxField(max_length=100000)
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    tags = TaggableManager(blank=True)
    is_published = models.BooleanField(default=False)
    for_lesson_complete = models.BooleanField(default=False)
    # 画像を添付する
        # works just like django's ImageField
    article_image_1 = StdImageField(
        upload_to='def_i/img',
        null=True,
        blank=True,
        variations={'thumbnail': {'width': 300, 'height': 225,"crop": True}},
        validators=[validate_image_file_extension]
    )
    article_image_2 = StdImageField(
        upload_to="def_i/img",
        null=True,
        blank=True,
        variations={'thumbnail': {'width': 300, 'height': 225,"crop": True}},
        validators=[validate_image_file_extension]
    )

    def __str__(self):
        return str(self.title)

    def formatted_markdown(self):
        return markdownify(self.content)


class Question(models.Model):
    poster = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="user_question", null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="category_question", null=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, related_name="course_question", null=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, related_name="lesson_question", null=True)
    title = models.CharField(max_length=30)
    # content = models.TextField(null=True)
    content = MarkdownxField(max_length=100000)
    is_answered = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    tags = TaggableManager(blank=True)
    # 画像を添付する
    question_image_1 = StdImageField(
        upload_to='def_i/img',
        null=True,
        blank=True,
        variations={'thumbnail': {'width': 300, 'height': 225,"crop": True}},
        validators=[validate_image_file_extension]
    )
    question_image_2 = StdImageField(
        upload_to="def_i/img",
        null=True,
        blank=True,
        variations={'thumbnail': {'width': 300, 'height': 225,"crop": True}},
        validators=[validate_image_file_extension]
    )

    bookmark_count = models.PositiveIntegerField(default=0)

    def browser_push(self):
        data = {
            'app_id':'ea35df03-ba32-4c85-9f7e-383106fb1d24',
            'safari_web_id': "web.onesignal.auto.47a2f439-afd3-4bb7-8cdd-92cc4f5ee46c",
            'included_segments': ['All'],
            'contents': {'en': self.title},
            'headings': {'en': '新しい質問が投稿されました！質問に答えましょう．'},
            'url': resolve_url('question_feed'),
        }
        requests.post(
            "https://onesignal.com/api/v1/notifications",
            headers={'Authorization': ONESIGNAL_SECRET_KEY},
            json=data,
        )

    def notify_new_question(self):
        line_bot_api = LineBotApi(channel_access_token=LINE_CHANNEL_ACCESS_TOKEN)
        notify_to = LineFriend.objects.filter(is_answerer=True)
        for push in notify_to:
            line_bot_api.push_message(push.line_user_id, TextSendMessage(text=f" 【{self.category}】 の質問 【{self.title}】 が投稿されました。回答をお願いします。"))

    def formatted_markdown(self):
        return markdownify(self.content)

    def __str__(self):
        return str(self.title)


class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    has_noticed = models.BooleanField(default=False)


class BookMark(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    has_noticed = models.BooleanField(default=False)


class Talk(models.Model):
    msg = models.TextField(max_length=1000)
    msg_from = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="msg_from",null=True)
    msg_to = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="msg_to",null=True)
    time = models.DateTimeField(auto_now_add=True)
    has_noticed = models.BooleanField(default=False)
    # def __str__(self):
    #     return "{}から{}へのメッセージ".format(self.msg_from,self.msg_to)


CATEGORY_CHOICE = (
    ('記事','記事'),
    ('質問','質問'),
)


class TalkAtArticle(Talk):
    msg_at = models.ForeignKey(Article, on_delete=models.CASCADE)
    category = models.CharField(max_length=10,
        choices=CATEGORY_CHOICE, default='記事')

    def notify_new_comment(self):
        line_bot_api = LineBotApi(channel_access_token=LINE_CHANNEL_ACCESS_TOKEN)
        other_commenters = TalkAtArticle.objects.filter(msg_at=self.msg_at).values("msg_from")  # 同じ記事にコメントした人全員に通知？
        notify_to = LineFriend.objects.filter(Q(user=self.msg_to)|Q(user__in=other_commenters)).exclude(user=self.msg_from)
        print("to:", notify_to)
        for push in notify_to:
            if push.notify_comment:
                if push.user == self.msg_at.poster:
                    line_bot_api.push_message(
                        push.line_user_id,
                        TextSendMessage(text=f"あなたの 【{self.msg_at.category}】 のノート 【{self.msg_at}】 にコメントが来ました。")
                    )
                else:
                    line_bot_api.push_message(
                        push.line_user_id,
                        TextSendMessage(text=f"あなたがコメントした 【{self.msg_at.category}】 のノート 【{self.msg_at}】 にコメントが来ました。")
                    )


class TalkAtQuestion(Talk):
    msg_at = models.ForeignKey(Question, on_delete=models.CASCADE)
    category = models.CharField(max_length=10,
        choices=CATEGORY_CHOICE, default='質問')

    def notify_new_comment(self):
        line_bot_api = LineBotApi(channel_access_token=LINE_CHANNEL_ACCESS_TOKEN)
        other_commenters = TalkAtQuestion.objects.filter(msg_at=self.msg_at).values("msg_from")  # 同じ質問にコメントした人全員に通知？
        notify_to = LineFriend.objects.filter(Q(user=self.msg_to)|Q(user__in=other_commenters)).exclude(user=self.msg_from) #投稿者か，その質問でコメントしてる人,かつ今コメントした人以外
        for push in notify_to:
            if push.notify_answer:
                if push.user == self.msg_at.poster:
                    line_bot_api.push_message(
                        push.line_user_id,
                        TextSendMessage(text=f"あなたの 【{self.msg_at.category}】 の質問 【{self.msg_at}】 にコメントが来ました。")
                    )
                else:
                    line_bot_api.push_message(
                        push.line_user_id,
                        TextSendMessage(text=f"あなたが回答した 【{self.msg_at.category}】 の質問 【{self.msg_at}】 にコメントが来ました。")
                    )

    def __str__(self):
        return f"FROM {self.msg_from} TO {self.msg_to} AT {self.msg_at}"


class LineFriend(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # unique=True?
    line_user_id = models.CharField(max_length=100)
    is_intern = models.BooleanField(default=False)
    is_answerer = models.BooleanField(default=False)

    notify_comment = models.BooleanField(default=True)
    notify_answer = models.BooleanField(default=True)

    def __str__(self):
        return f"Line Friend: {self.user}, is_intern = {self.is_intern}"
