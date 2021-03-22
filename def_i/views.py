from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, LogoutView
)
from django.views.generic import ListView,DetailView,FormView
from django.views.generic.edit import FormMixin
from .forms import LoginForm, ArticleTalkForm
from .models import User,Article,TalkAtArticle


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
    def get_queryset(self): #queryset=だけでいいことが判明
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
    # form_class = ArticleTalkForm

class ArticleTalk(FormMixin,ListView):
    model = TalkAtArticle
    context_object_name = "messages"
    form_class = ArticleTalkForm
    template_name = 'def_i/article_talk.html'
    success_url = 'def_i/index.html'
    # success_url =
    def get(self,request,pk):
        form = ArticleTalkForm()
        article = Article.objects.get(pk=pk)
        messages = TalkAtArticle.objects.filter(msg_at=article).order_by('-time')
        return render(request,self.template_name,{"messages":messages,"form":form})
    def post(self,request,pk,*args,**kwargs):
        form = ArticleTalkForm(request.POST)
        if form.is_valid():
            messages = form.cleaned_data.get('msg')
            article = Article.objects.get(pk=pk)
            article_poster = User.objects.get(pk=article.poster.id)
            msg = self.model.objects.create(msg=messages,msg_from = request.user,msg_to = article_poster,msg_at=article)
            msg.save()
        return render(request,self.template_name,{"form":form})





class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'def_i/login.html'


class Logout(LogoutView):
    """ログアウトページ"""
    template_name = 'def_i/top.html'
