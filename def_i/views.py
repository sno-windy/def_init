from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, LogoutView
)
from django.views import generic
from .forms import LoginForm


def index(request):
    return render(request,"def_i/index.html")

class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'def_i/login.html'


class Logout(LogoutView):
    """ログアウトページ"""
    template_name = 'def_i/top.html'

