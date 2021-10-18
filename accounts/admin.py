from django.contrib import admin
from .models import User
from def_i.models import *

class UserAdmin(admin.ModelAdmin):
    def cleared_lesson(self,request):
        # studying_category = Category.objects.filter(
        #     studying_category__user=request.pk)[:1]

        # studying_course = Course.objects.filter(
        #     category=studying_category)

        cleared_lesson = ClearedLesson.objects.filter(
            user=request.pk).order_by('-cleared_at')

        # # 値がない場合の初期化
        # last_cleared_lesson = 0
        # last_cleared_course = 0
        # next_lesson_num = 1
        # next_course_num = 1

        last_cleared_lesson = cleared_lesson.first()
        # if cleared_lesson.len() >= 2:
        #     interval =

        # # last_cleared_lesson の値があるなら
        # if  not ((l := last_cleared_lesson) == None):
        #     last_cleared_course = l.lesson.course.course_num
        #     next_lesson_num = l.lesson.lesson_num + 1

        # next_lesson = Lesson.objects.filter(course__in=studying_course, lesson_num=next_lesson_num,
        #                                     course__course_num=last_cleared_course).first()
        # learning_lesson = next_lesson

        # # next_lesson が見つからないなら
        # if next_lesson == None:

        #     next_course_num = last_cleared_course + 1

        #     next_course = Course.objects.filter(
        #         category=studying_category, course_num=next_course_num).first()

        #     learning_lesson = Lesson.objects.filter(
        #         course__in=studying_course, course=next_course, lesson_num=1).first()

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
    # ordering = ('cleared_lesson_time',)

admin.site.register(User,UserAdmin)
