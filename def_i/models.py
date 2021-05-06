from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill
from taggit.managers import TaggableManager
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.shortcuts import resolve_url
from def_init.secret_settings import *
import requests

User = get_user_model()


# COURSE_CATEGORY_CHOICE = (
#     ('backend','backend'),
#     ('frontend','frontend'),
#     ('design','design')
# )
class Category(models.Model):
    title = models.CharField(max_length=10)
    category_image = ProcessedImageField(upload_to="def_i/img",
        processors=[ResizeToFill(250,250)],
        format='JPEG',
        options={'quality':60},
        blank=True
        )
    description = models.TextField(max_length=100, null=True)

class Course(models.Model):
    title = models.CharField(max_length=30)
    course_num = models.PositiveSmallIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.title)


class Lesson(models.Model):
    title = models.CharField(max_length=30)
    contents = models.TextField(max_length=1000, null=True)
    lesson_num = models.PositiveSmallIntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="lessons")

    def __str__(self):
        return str(self.title)


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
        return f"{self.user} now studying {self.course_category}"


class Article(models.Model):
    poster = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="user_article",null=True)
    article_at = models.ForeignKey(Lesson, on_delete=models.SET_NULL, related_name="lesson_article",null=True)
    title = models.CharField(max_length=30)
    content = MarkdownxField()
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    tags = TaggableManager(blank=True)
    is_published = models.BooleanField(default=False)
    # 画像を添付する
    article_image_1 = models.ImageField(upload_to="def_i/img",null=True)
    article_image_2 = models.ImageField(upload_to="def_i/img",null=True)
    article_image_1_resize = ImageSpecField(source='user_image_1',
        processors=[ResizeToFill(250,250)],
        format='JPEG',
        options={'quality':60}
        )
    article_image_2_resize = ImageSpecField(source='user_image_2',
        processors=[ResizeToFill(250,250)],
        format='JPEG',
        options={'quality':60}
        )

    def __str__(self):
        return str(self.title)

    def formatted_markdown(self):
        return markdownify(self.content)


class Question(models.Model):
    poster = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="user_question",null=True)
    question_at = models.ForeignKey(Lesson, on_delete=models.SET_NULL, related_name="lesson_question",null=True)
    title = models.CharField(max_length=30)
    # content = models.TextField(null=True)
    content = MarkdownxField()
    if_answered = models.BooleanField(default=False) #->is_answered
    created_at = models.DateTimeField(default=timezone.now)
    tags = TaggableManager(blank=True)

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
            headers={'Authorization': ONESIGNAL_SECRET_KEY},
            json=data,
        )

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


class TalkAtQuestion(Talk):
    msg_at = models.ForeignKey(Question, on_delete=models.CASCADE)
    category = models.CharField(max_length=10,
        choices=CATEGORY_CHOICE, default='質問')

    def __str__(self):
        return f"FROM {self.msg_from} TO {self.msg_to} AT {self.msg_at}"
