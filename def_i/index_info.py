import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Count, OuterRef, Subquery
from django.utils.timezone import make_aware

from .models import *



class GetIndexInfo:
    def __init__(self, user):
        # 他の情報取得に使うため、進行中のコースを取得
        self.studying_category = Category.objects.filter(studying_category__user=user)[:1]

        self.studying_course = Course.objects.filter(category=self.studying_category)

        self.cleared_lesson = ClearedLesson.objects.filter(user=user).order_by('-cleared_at')

        #↓この辺三項式でやれば簡潔にできそうだね

        try:
            self.last_cleared_lesson = self.cleared_lesson[0]

            self.last_cleared_course = self.last_cleared_lesson.lesson.course.course_num

            next_lesson_num = self.last_cleared_lesson.lesson.lesson_num + 1

        except IndexError: #ひとつも取り組んでいない
            self.last_cleared_lesson = 0

            self.last_cleared_course = 0

            next_lesson_num = 1

            next_course_num = 1

        try:
            next_lesson = Lesson.objects.get(course__in=self.studying_course,lesson_num=next_lesson_num, course__course_num=self.last_cleared_course) #この場合ほしいのは一つなわけだから、filter().first()でいいよね

            self.learning_lesson = next_lesson

        except ObjectDoesNotExist:

            next_course_num = self.last_cleared_course + 1

            try:
                next_course = Course.objects.get(category=self.studying_category,course_num=next_course_num)

                self.learning_lesson = Lesson.objects.get(course__in=self.studying_course,course=next_course,lesson_num=1)
            except ObjectDoesNotExist:
                self.learning_lesson = None
        # try:
        #     self.last_cleared_lesson = self.cleared_lesson[0]
        #     next_lesson_num = self.last_cleared_lesson.lesson.lesson_num + 1
        # except IndexError:
        #     # まだ一つもレッスンを完了していない場合
        #     self.last_cleared_lesson = 0
        #     next_lesson_num = 1
        #     next_course_num = 1

        # try:
        #     next_course = Course.objects.get(course_num=next_course_num,category=self.studying_category)
        #     self.learning_lesson = Lesson.objects.get(lesson_num=next_lesson_num,course=next_course)
        # except ObjectDoesNotExist:
        #     # 全てのレッスンを完了した場合
        #     self.learning_lesson = 0



    # ユーザーのランキング情報を取得
    def get_ranking(self):
        date = make_aware(timezone.datetime.today())
        a_week_ago = date + datetime.timedelta(days=-7)
        print(a_week_ago)
        ranking = User.objects.annotate(
            cleared_lesson_num = Subquery(
                ClearedLesson.objects
                    .filter(user=OuterRef('pk'))
                    .filter(cleared_at__gte=a_week_ago)
                    .values('user')
                    .annotate(count = Count('pk'))
                    .values('count')
            ),
            note_num = Subquery(
                Article.objects
                    .filter(poster=OuterRef('pk'))
                    .filter(created_at__gte=a_week_ago)
                    .values('poster')
                    .annotate(count = Count('pk'))
                    .values('count')
            )
            # Noneのとき０にしたい

        ).order_by('-note_num').order_by('-cleared_lesson_num')[:3]  # 何位まで表示する？
        return ranking

    # 進捗状況を取得
    def get_progress(self, user):
        all_lesson = Lesson.objects.all()
        all_cleared_lesson = ClearedLesson.objects.filter(user=user)
        course = Course.objects.all()
        category_list = Category.objects.all()
        progress_percent_list = []

        #category毎の達成率を表示
        for category in category_list:
            course = Course.objects.filter(category=category)
            lesson = all_lesson.filter(course__in=course)
            lesson_count = lesson.count()
            cleared_lesson_count = all_cleared_lesson.filter(lesson__in=lesson).count()

            if lesson:
                progress_percent = round(cleared_lesson_count * 100 / lesson_count,1)
            else:
                progress_percent = 0.0

            progress_percent_list.append(progress_percent)
        progress_zip = [[cat,per] for cat,per in zip(category_list,progress_percent_list)]
        all_lesson_count = all_lesson.count()
        my_cleared_lesson_num = self.cleared_lesson.count()
        progress_decimal = my_cleared_lesson_num / all_lesson_count if all_lesson_count else 0.0
        progress_percent = progress_decimal * 100
        return progress_percent,progress_zip


    # 進行中のコースに関連した質問を取得
    def get_related_questions(self):
        related_questions = Question.objects.filter(lesson=self.learning_lesson).order_by('-created_at')[:6]
        return related_questions

    # 進行中のコースに関連したノートを取得
    def get_related_articles(self):
        related_articles = Article.objects.filter(lesson=self.learning_lesson).order_by('-created_at')[:6]  # 並べる順番
        return related_articles

    # 進捗が近いユーザーを取得
    def get_colleagues(self, user):
        if self.last_cleared_lesson:
            colleague_data = User.objects.annotate(
                colleague_studying = Subquery(
                    StudyingCategory.objects.filter(user=OuterRef('pk'))
                        .values('category')[:1]
                )
            ).filter(cleared_user__lesson=self.last_cleared_lesson.lesson).exclude(cleared_user__user=user).order_by('-cleared_user__cleared_at').prefetch_related('studying_category_set')[:3]

            return colleague_data
        else:
            colleague_data = User.objects.filter(cleared_user__isnull=True).exclude(username=user)
            return colleague_data


# お知らせを取得
    def get_notification(self, user):
        # 記事へのいいね
        new_likes = Like.objects.filter(article__poster=user, has_noticed=False)
        new_bookmarks = BookMark.objects.filter(question__poster=user, has_noticed=True)
        # 記事へのコメント
        article_talk = TalkAtArticle.objects.filter(msg_to=user, has_noticed=False).order_by('-time')
        # 質問へのコメント
        question_talk = TalkAtQuestion.objects.filter(msg_to=user, has_noticed=False).order_by('time')

        for like in new_likes:
            like.has_noticed = True
            like.save()
        for bookmark in new_bookmarks:
            bookmark.has_noticed = True
            bookmark.save()
        for talk in article_talk:
            talk.has_noticed = True
            talk.save()
        for talk in question_talk:
            talk.has_noticed = True
            talk.save()

        return new_likes, new_bookmarks, article_talk, question_talk

    # def get_course_list(self,user,category):
    #     courses = Course.objects.filter(category__title=category).order_by('course_num')
    #     progress_percent_list = []
    #     for course in courses:
    #         lessons = Lesson.objects.
    #         cleared_lessons = ClearedLesson.objects.filter(user=user,lesson__in=lessons)
    #         if lessons:
    #             progress_percent = round(cleared_lessons * 100 / lessons,1)
    #             progress_percent_list.append(progress_percent)
    #     print(progress_percent_list)
    #     return courses
