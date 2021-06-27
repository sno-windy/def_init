from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.login,name='account_login'),
    path('signup/',views.signup, name='account_signup'),
    path('logout/',views.logout, name='account_logout'),
    path('change/', views.change, name='account_change'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('social/signup',views.SocialSignupView.as_view(), name="account_social_signup")
]
