from django.db.models import Count
from .models import *


class GetIndexInfo:
    def __init__(self, user):
        # 他の情報取得に使うため、進行中のコースを取得
        self.studying_category = Category.objects.filter(
            studying_category__user=user)[:1]

        self.studying_course = Course.objects.filter(
            category=self.studying_category)

        self.cleared_lesson = ClearedLesson.objects.filter(
            user=user).order_by('-cleared_at')

        # 値がない場合の初期化
        self.last_cleared_lesson = 0
        self.last_cleared_course = 0
        next_lesson_num = 1
        next_course_num = 1

        self.last_cleared_lesson = self.cleared_lesson.first()

        # self.last_cleared_lesson の値があるなら
        if  not ((l := self.last_cleared_lesson) == None):
            self.last_cleared_course = l.lesson.course.course_num
            next_lesson_num = l.lesson.lesson_num + 1

        next_lesson = Lesson.objects.filter(course__in=self.studying_course, lesson_num=next_lesson_num,
                                            course__course_num=self.last_cleared_course).first()
        self.learning_lesson = next_lesson

        # next_lesson が見つからないなら
        if next_lesson == None:

            next_course_num = self.last_cleared_course + 1

            next_course = Course.objects.filter(
                category=self.studying_category, course_num=next_course_num).first()

            self.learning_lesson = Lesson.objects.filter(
                course__in=self.studying_course, course=next_course, lesson_num=1).first()

    # ユーザーのランキング情報を取得
    def get_ranking(self, user):
        # date = make_aware(timezone.datetime.today())
        # a_week_ago = date + datetime.timedelta(days=-7)
        ranking = User.objects.annotate(
            Count("cleared_user",distinct=True),
            Count("user_article",distinct=True)
        ).order_by('-cleared_user__count','-user_article__count')  # 何位まで表示する？.
        print(ranking)
        ranking_zip = list(zip(range(1, len(ranking)+1), ranking))

        top_ranking = ranking_zip[:3]
        user_rank = -1
        for index, obj in ranking_zip:
            if obj == user:
                user_rank = index  # userの順位
        if user_rank == 1:
            user_ranking = top_ranking
        elif user_rank <= 0:
            return IndexError
        elif user_rank == len(ranking):
            if len(ranking) >= 3:
                user_ranking = ranking_zip[user_rank-3:user_rank]
            else:
                user_ranking = top_ranking
        else:
            user_ranking = ranking_zip[user_rank-2:user_rank+1]
        return top_ranking, user_ranking

    # 進捗状況を取得
    def get_progress(self, user):
        all_lesson = Lesson.objects.all()
        all_cleared_lesson = ClearedLesson.objects.filter(user=user)
        category_list = Category.objects.all()
        progress_percent_list = []

        # category毎の達成率を表示
        for category in category_list:
            course = Course.objects.filter(category=category)
            lesson = all_lesson.filter(course__in=course)
            lesson_count = lesson.count()
            cleared_lesson_count = all_cleared_lesson.filter(
                lesson__in=lesson).count()

            if lesson:
                progress_percent = round(
                    cleared_lesson_count * 100 / lesson_count, 1)
            else:
                progress_percent = 0.0

            progress_percent_list.append(progress_percent)
        progress_zip = [[cat, per]
                        for cat, per in zip(category_list, progress_percent_list)]
        all_lesson_count = all_lesson.count()
        my_cleared_lesson_num = self.cleared_lesson.count()
        progress_decimal = my_cleared_lesson_num / all_lesson_count if all_lesson_count else 0.0
        progress_percent = progress_decimal * 100
        return progress_percent, progress_zip

    # 進行中のコースに関連した質問を取得

    def get_related_questions(self):
        related_questions = Question.objects.filter(
            lesson__course__category=self.studying_category).order_by('-created_at')[:5]
        return related_questions

    # 進行中のコースに関連したノートを取得
    def get_related_articles(self):
        related_articles = Article.objects.filter(
            lesson__course__category=self.studying_category, is_published=True).order_by('-created_at')[:5]  # 並べる順番
        return related_articles

    # 進捗が近いユーザーを取得
    def get_colleagues(self, user):
        if self.studying_category:
            studying = list(self.studying_category)[0]
        else:
            studying = None
        if self.last_cleared_lesson:
            colleague_list = User.objects.filter(cleared_user__lesson=self.last_cleared_lesson.lesson).exclude(cleared_user__user=user).order_by('-cleared_user__cleared_at')[:3]

        # colleagueの進捗情報をとってきている。
            colleague_studying_progress = []

            for data in colleague_list:
                _, colleague_progress = self.get_progress(data)
                for co in colleague_progress:
                    if co[0] == studying:
                        colleague_studying_progress.append(co[1])
            colleague_data = [[colleague, prog] for colleague, prog in zip(
                colleague_list, colleague_studying_progress)]

            return colleague_data

        else:
            colleague_data = None
            return colleague_data


# お知らせを取得

    def get_notification(self, user):
        # 記事へのいいね
        new_likes = Like.objects.filter(
            article__poster=user, has_noticed=False)
        new_bookmarks = BookMark.objects.filter(
            question__poster=user, has_noticed=False)
        # 記事へのコメント
        article_talk = TalkAtArticle.objects.exclude(msg_from=user).filter(
            msg_to=user, has_noticed=False).order_by('-time')
        # 質問へのコメント
        question_talk = TalkAtQuestion.objects.exclude(msg_from=user).filter(
            msg_to=user, has_noticed=False).order_by('time')

        return new_likes, new_bookmarks, article_talk, question_talk
