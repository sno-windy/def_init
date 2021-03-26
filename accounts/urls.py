from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.login,name='account_login'),
    path('signup/',views.signup, name='account_signup'),
    path('logout/',views.logout, name='account_logout'),
    
]