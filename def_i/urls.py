from django.urls import path
from . import views
from . import sitemaps
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

sitemaps = {
'index': sitemaps.IndexSitemap,
}

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('ranking/', views.RankingView.as_view(), name='ranking'),

    # 記事系
    path('article_feed/',views.ArticleFeed.as_view(), name='article_feed'),
    path('article_detail/<int:pk>/',views.ArticleDetail.as_view(),name="article_detail"),
    path('article_post/',views.ArticlePost.as_view(),name='article_post'),
    path('article_post/<int:pk>/',views.ArticlePost.as_view(),name='article_post'),
    path('article_published/<int:pk>/', views.ArticlePublishedView.as_view(), name='article_published'),
    path('article_saved/<int:pk>/', views.ArticleSavedView.as_view(), name='article_saved'),
    path('article_failed/', views.ArticlePostFailed.as_view(), name="article_failed"),
    path('article_edit/<int:pk>/',views.ArticleUpdateView.as_view(),name='article_edit'),
    path('article_delete/<int:pk>/',views.ArticleDeleteView.as_view(),name='article_delete'),

    # 質問系
    path('question_feed/',views.QuestionFeed.as_view(),name='question_feed'),
    path('question_detail/<int:pk>/',views.QuestionDetail.as_view(),name='question_detail'),
    path('question_failed/', views.QuestionPostFailed.as_view(), name="question_failed"),
    path('question_post_suc/<int:pk>/',views.QuestionPostSuc.as_view(),name='question_post_suc'),
    path('question_post/',views.QuestionPost.as_view(),name='question_post'),
    path('question_edit/<int:pk>/',views.QuestionUpdateView.as_view(),name='question_edit'),
    path('question_delete/<int:pk>/',views.QuestionDeleteView.as_view(),name='question_delete'),

    # コース系
    path('course/', views.course, name="course"),
    path('course/<str:category>/',views.CourseList.as_view(),name='course_list'),
    path('mark_as_studying/', views.mark_as_studying, name="mark_as_studying"),
    path('task_detail/<str:category>/<int:course_num>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('task_detail/<str:category>/<int:course_num>/<int:lesson_num>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('task_detail/<int:pk>/question', views.TaskQuestion.as_view(), name='task_question'),
    path('task_detail/<int:pk>/question/post', views.TaskQuestionPost.as_view(), name='task_question_post'),
    path('task_detail/<int:pk>/article/post', views.TaskArticlePost.as_view(), name='task_article_post'),
    path('task_detail/<int:pk>/article_for_complete/post', views.TaskCompleteArticlePost.as_view(), name="task_complete_article"),
    path('task_detail/<int:pk>/article_for_complete_edit/', views.TaskCompleteArticleUpdate.as_view(), name="task_complete_article_edit"),
    path('task_detail/<int:pk>/article', views.TaskArticle.as_view(), name='task_article'),
    path('note_list/', views.note_list, name='note_list'),
    path('complete/<int:pk>/', views.lesson_complete, name="complete"),

    # マイページ系
    path('message_notification/',views.MessageNotification.as_view(),name='message_notification'),
    path('like/<int:pk>/',views.LikeView,name='like'),
    path('bookmark/<int:pk>/', views.BookMarkView, name='bookmark'),
    path('user_page/<int:pk>/',views.userpage_view,name='user_page'),
    path('my_page/',views.mypage_view,name="my_page"),

    # LINE関連
    path('callback/', views.callback, name='callback'),

    #robots
    path('robots.txt',TemplateView.as_view(template_name='def_i/robots.txt', content_type='text/plain')),

    #sitemaps
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    #notify
    path('notify_bell', views.notify, name="notify_bell"),

]
