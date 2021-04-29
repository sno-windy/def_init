from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Count, OuterRef, Subquery

from .models import *


class GetIndexInfo:
    def __init__(self, user):
        # 他の情報取得に使うため、進行中のコースを取得
        self.cleared_lesson = ClearedLesson.objects.filter(user=user).order_by('-cleared_at')
        try:
            self.last_cleared_lesson = self.cleared_lesson[0]
            next_lesson_num = self.last_cleared_lesson.lesson.lesson_num + 1
        except IndexError:
            # まだ一つもレッスンを完了していない場合
            self.last_cleared_lesson = None
            next_lesson_num = 1

        try:
            self.learning_lesson = Lesson.objects.get(lesson_num=next_lesson_num)
        except ObjectDoesNotExist:
            # 全てのレッスンを完了した場合
            self.learning_lesson = None



    # ユーザーのランキング情報を取得
    def get_ranking(self):
        ranking = User.objects.annotate(
            cleared_lesson_num = Subquery(
                ClearedLesson.objects
                    .filter(user=OuterRef('pk'))
                    .values('user')
                    .annotate(count = Count('pk'))
                    .values('count')
            ),
            note_num = Subquery(
                Article.objects
                    .filter(poster=OuterRef('pk'))
                    .values('poster')
                    .annotate(count = Count('pk'))
                    .values('count')
            )
            # Noneのとき０にしたい

        ).order_by('-note_num').order_by('-cleared_lesson_num')[:6]  # 何位まで表示する？
        return ranking

    # 進捗状況を取得
    def get_progress(self, user):
        all_lesson = Lesson.objects.all().count()
        my_cleared_lesson_num = self.cleared_lesson.count()
        progress_decimal = my_cleared_lesson_num / all_lesson
        progress_percent = progress_decimal * 100
        return progress_percent


    # 進行中のコースに関連した質問を取得
    def get_related_questions(self):
        related_questions = Question.objects.filter(question_at=self.learning_lesson).order_by('-created_at')[:6]
        return related_questions

    # 進行中のコースに関連したノートを取得
    def get_related_articles(self):
        related_articles = Article.objects.filter(article_at=self.learning_lesson).order_by('-created_at')[:6]  # 並べる順番
        return related_articles

    # 進捗が近いユーザーを取得
    def get_colleagues(self, user):
        if self.last_cleared_lesson:
            colleague_data = User.objects.filter(cleared_user__lesson=self.last_cleared_lesson.lesson).exclude(cleared_user__user=user).order_by('-cleared_user__cleared_at')[:6]
            return colleague_data
        else:
            colleague_data = User.objects.filter(cleared_user__isnull=True).exclude(username=user)
            return colleague_data


# お知らせを取得
    def get_notification(self, user):
        # 記事へのいいね
        new_likes = Like.objects.filter(article__poster=user, has_noticed=False)
        # 記事へのコメント
        article_talk = TalkAtArticle.objects.filter(msg_to=user, has_noticed=False).order_by('-time')
        # 質問へのコメント
        question_talk = TalkAtQuestion.objects.filter(msg_to=user, has_noticed=False).order_by('time')

        for like in new_likes:
            like.has_noticed = True
            like.save()
        for talk in article_talk:
            talk.has_noticed = True
            talk.save()
        for talk in question_talk:
            talk.has_noticed = True
            talk.save()

        return new_likes, article_talk, question_talk
