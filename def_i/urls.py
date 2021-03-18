from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('',views.index,name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout')
]
