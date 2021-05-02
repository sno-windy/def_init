from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    # 記事系
    path('article_feed/',views.ArticleFeed.as_view(), name='article_feed'),
    # path('article_feed_like/',views.ArticleFeedLike.as_view(), name='article_feed_like'),
    path('article_detail/<int:pk>/',views.ArticleDetail.as_view(),name="article_detail"),
    path('article_talk/<int:pk>/',views.ArticleTalk.as_view(),name="article_talk"),
    path('article_talk_suc/<int:pk>/',views.ArticleTalkSuc.as_view(),name='article_talk_suc'),
    path('article_post/',views.ArticlePost.as_view(),name='article_post'),
    path('article_edit/<int:pk>/',views.ArticleUpdateView.as_view(),name='article_edit'),
    path('article_delete/<int:pk>/',views.ArticleDeleteView.as_view(),name='article_delete'),

    # 質問系
    path('question_feed/',views.QuestionFeed.as_view(),name='question_feed'),
    # path('question_feed_unanswered/',views.QuestionFeedUnanswered.as_view(),name='question_feed_unanswered'),
    path('question_detail/<int:pk>/',views.QuestionDetail.as_view(),name='question_detail'),
    path('question_talk/<int:pk>/',views.QuestionTalk.as_view(),name='question_talk'),
    path('question_talk_suc/<int:pk>/',views.QuestionTalkSuc.as_view(),name='question_talk_suc'),
    path('question_post/',views.QuestionPost.as_view(),name='question_post'),
    path('question_edit/<int:pk>/',views.QuestionUpdateView.as_view(),name='question_edit'),
    path('question_delete/<int:pk>/',views.QuestionDeleteView.as_view(),name='question_delete'),

    # コース系
    path('course/', views.course, name="course"),
    path('task_backend/',views.BackendTaskList.as_view(),name='task_backend'),
    path('task_backend/<int:pk>/', views.TaskDetail.as_view(), name='task_detail'),
    # path('task_backend/<int:pk>/memo', views.MemoView, name='task_memo'),
    path('task_backend/<int:pk>/question', views.TaskQuestion.as_view(), name='task_question'),
    # path('task_backend/<int:pk>/question_unanswered', views.TaskQuestionUnanswered.as_view(), name='task_question_unanswered'),
    path('task_backend/<int:pk>/question/post', views.TaskQuestionPost.as_view(), name='task_question_post'),
    path('task_backend/<int:pk>/article/post', views.TaskArticlePost.as_view(), name='task_article_post'),
    path('task_backend/<int:pk>/article', views.TaskArticle.as_view(), name='task_article'),
    # path('task_backend/<int:pk>/article_like', views.TaskArticleLike.as_view(), name='task_article_like'),
    path('task_frontend/',views.FrontendTaskList.as_view(),name='task_frontend'),
    path('note_list/', views.note_list, name = 'note_list'),

    # マイページ系
    path('message_notification/',views.MessageNotification.as_view(),name='message_notification'),
    path('like/<int:pk>/',views.LikeView,name='like'),
    path('user_page/<int:pk>/',views.UserPageView.as_view(),name='user_page'),
    path('my_page/',views.MyPageView.as_view(),name="my_page"),

    # LINE関連
    path('new_line_friend/', views.new_line_friend, name='new_line_friend'),
]
