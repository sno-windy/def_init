from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Article, Question, Like, Task, Talk, TalkAtArticle, TalkAtQuestion

admin.site.register(User, UserAdmin)
admin.site.register(Article)
admin.site.register(Question)
admin.site.register(Like)
admin.site.register(Task)
admin.site.register(Talk)
admin.site.register(TalkAtQuestion)
admin.site.register(TalkAtArticle)
