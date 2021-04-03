from .models import  Article, Question, Like, Task, Talk, TalkAtArticle, TalkAtQuestion, Memo, Task_Sub
from django.contrib import admin

admin.site.register(Article)
admin.site.register(Question)
admin.site.register(Like)
admin.site.register(Task)
admin.site.register(Task_Sub)
admin.site.register(Talk)
admin.site.register(TalkAtQuestion)
admin.site.register(TalkAtArticle)
admin.site.register(Memo)
