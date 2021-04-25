from .models import  Article, Question, Like, Course, Talk, TalkAtArticle, TalkAtQuestion, Memo, Lesson, ClearedLesson
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
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Talk)
admin.site.register(TalkAtQuestion)
admin.site.register(TalkAtArticle)
admin.site.register(Memo)
admin.site.register(ClearedLesson)
