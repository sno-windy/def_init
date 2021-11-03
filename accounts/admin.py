from django.contrib import admin
from .models import User
from def_i.models import *

class UserAdmin(admin.ModelAdmin):
    def cleared_lesson(self,request):
        cleared_lesson = ClearedLesson.objects.filter(
            user=request.pk).order_by('-cleared_at')

        last_cleared_lesson = cleared_lesson.first()

        return last_cleared_lesson


    def cleared_lesson_time(self,request):
        cleared_lesson = ClearedLesson.objects.filter(
            user=request.pk).order_by('-cleared_at')
        last_cleared_lesson = cleared_lesson.first()
        if (c := last_cleared_lesson):
            cleared_lesson_time = c.cleared_at
        else:
            cleared_lesson_time = None
        return cleared_lesson_time
    cleared_lesson.short_description = 'last_cleared_lesson'
    cleared_lesson_time.short_description = 'cleared_lesson_time'

    list_display = ('username', 'date_joined', 'position','cleared_lesson','cleared_lesson_time')

admin.site.register(User,UserAdmin)
