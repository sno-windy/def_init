from .models import  Article, Question, Like, Task, Talk, TalkAtArticle, TalkAtQuestion, Memo, Task_Sub
from django.contrib import admin

def notify(modeladmin,request,queryset):
    for q in queryset:
        q.browser_push(request)

class QuestionAdmin(admin.ModelAdmin):
    actions = [notify]

admin.site.register(Article)
notify.short_description = '通知を送信する'
admin.site.register(Question, QuestionAdmin)
admin.site.register(Like)
admin.site.register(Task)
admin.site.register(Task_Sub)
admin.site.register(Talk)
admin.site.register(TalkAtQuestion)
admin.site.register(TalkAtArticle)
admin.site.register(Memo)
