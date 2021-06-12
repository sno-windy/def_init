from .models import  *
from django.contrib import admin
from django.contrib.sites.models import Site

def notify(request,queryset):
    for q in queryset:
        q.browser_push(request)

class QuestionAdmin(admin.ModelAdmin):
    actions = [notify]

class LessonAdmin(admin.ModelAdmin):
    ordering = ('course','lesson_num')

class CourseAdmin(admin.ModelAdmin):
    ordering = ('category','course_num')

admin.site.register(Article)
notify.short_description = '通知を送信する'
admin.site.register(Question, QuestionAdmin)
admin.site.register(Like)
admin.site.register(Course,CourseAdmin)
admin.site.register(Category)
admin.site.register(StudyingCategory)
admin.site.register(Lesson,LessonAdmin)
admin.site.register(Talk)
admin.site.register(TalkAtQuestion)
admin.site.register(TalkAtArticle)
admin.site.register(ClearedLesson)
admin.site.register(LineFriend)

admin.site.unregister(Site)
class SiteAdmin(admin.ModelAdmin):
     list_display = ('id', 'domain', 'name')

admin.site.register(Site, SiteAdmin)