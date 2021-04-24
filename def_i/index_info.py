from django.db.models import Count, OuterRef, Subquery

from .models import Lesson, ClearedLesson, User, Memo

# ユーザーのランキング情報を取得
    # コースの完了率とノートの投稿回数で判断
def get_ranking():
    # ここでログインユーザーの進捗率も取得すればいい
    ranking = User.objects.annotate(
        cleared_lesson_num = Subquery(
            ClearedLesson.objects.filter(user=OuterRef('pk')).values('user').annotate(count = Count('pk')).values('count')
        ),
        note_num = Subquery(
            Memo.objects.filter(relate_user=OuterRef('pk')).values('relate_user').annotate(count = Count('pk')).values('count')
        )

    ).order_by('-cleared_lesson_num').order_by('-note_num')
    print(ranking)
    for user in ranking:
        print(user, "cleared ", user.cleared_lesson_num)
        print(user, "wrote ", user.note_num)

    return ranking

# 進行中のコースを取得
# 進捗状況を取得
def get_progress(user):
    all_lesson = Lesson.objects.all().count()
    cleared_lesson = ClearedLesson.objects.filter(user=user).count()
    print(all_lesson)
    print(cleared_lesson)
    print(cleared_lesson / all_lesson)
    return cleared_lesson / all_lesson


# 進行中のコースに関連した質問を取得

# 進行中のコースに関連したノートを取得

# 進捗が近いユーザーを取得

# お知らせを取得
# def get_notification():

    # return new_notifications
