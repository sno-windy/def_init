from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('',views.index,name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('article_feed/',views.ArticleFeed.as_view(), name='article_feed'),
    path('article_feed_like/',views.ArticleFeedLike.as_view(), name='article_feed_like'),
    path('article_detail/<int:pk>/',views.ArticleDetail.as_view(),name="article_detail"),

]
