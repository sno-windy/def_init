from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, LogoutView
)
from django.views.generic import ListView,DetailView
from .forms import LoginForm
from .models import User,Article


def index(request):
    return render(request,"def_i/index.html")


class ArticleFeed(ListView):
    model = Article
    context_object_name = "articles"
    template_name = "def_i/article_feed.html"
    paginate_by = 10

    def get_queryset(self):
        articles = Article.objects.order_by('-created_at')
        return articles

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['sort_by_new'] = True
        return context

class ArticleFeedLike(ArticleFeed):
    def get_queryset(self):
        articles = Article.objects.order_by('-like_count')
        return articles

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['sort_by_new'] = False
        return context

class ArticleDetail(DetailView):
    model = Article
    context_object_name = "contents"
    template_name = "def_i/article_detail.html"


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'def_i/login.html'


class Logout(LogoutView):
    """ログアウトページ"""
    template_name = 'def_i/top.html'
