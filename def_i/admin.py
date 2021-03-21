from .models import  Article, Question, Like, Task, Talk, TalkAtArticle, TalkAtQuestion
from django.contrib import admin

admin.site.register(Article)
admin.site.register(Question)
admin.site.register(Like)
admin.site.register(Task)
admin.site.register(Talk)
admin.site.register(TalkAtQuestion)
admin.site.register(TalkAtArticle)
