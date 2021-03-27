from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('',views.index,name='index'),
    path('article_feed/',views.ArticleFeed.as_view(), name='article_feed'),
    path('article_feed_like/',views.ArticleFeedLike.as_view(), name='article_feed_like'),
    path('article_detail/<int:pk>/',views.ArticleDetail.as_view(),name="article_detail"),
    path('article_talk/<int:pk>/',views.ArticleTalk.as_view(),name="article_talk"),
    path('article_talk_suc/<int:pk>/',views.ArticleTalkSuc.as_view(),name='article_talk_suc'),
    path('article_post/',views.ArticlePost.as_view(),name='article_post'),
    path('question_feed_new/',views.QuestionFeed.as_view(),name='question_feed_new'),
    path('question_feed_unanswered/',views.QuestionFeedUnanswered.as_view(),name='question_feed_unanswered'),
    path('question_detail/<int:pk>/',views.QuestionDetail.as_view(),name='question_detail'),
    path('question_talk/<int:pk>/',views.QuestionTalk.as_view(),name='question_talk'),
    path('question_talk_suc/<int:pk>/',views.QuestionTalkSuc.as_view(),name='question_talk_suc'),
    path('question_post/',views.QuestionPost.as_view(),name='question_post'),
    path('task_backend/',views.BackendTaskList.as_view(),name='task_backend'),
    path('task_frontend/',views.FrontendTaskList.as_view(),name='task_frontend'),
    path('message_notification/',views.MessageNotification.as_view(),name='message_notification'),
    path('like/<int:pk>/',views.LikeView,name='like'),
]
