from django.shortcuts import render,reverse,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, LogoutView
)
from django.views.generic import ListView,DetailView,FormView,TemplateView,CreateView
from django.views.generic.edit import FormMixin
from .forms import LoginForm, ArticleTalkForm, ArticlePostForm
from .models import User,Article,TalkAtArticle,Question,TalkAtQuestion

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
    model =TalkAtArticle
    context_object_name = "messages"
    form_class = ArticleTalkForm #いらんかも
    template_name = 'def_i/article_talk.html'
    def get(self,request,pk):
        form = ArticleTalkForm()
        article = Article.objects.get(pk=pk)
        messages = TalkAtArticle.objects.filter(msg_at=article).order_by('time')
        return render(request,self.template_name,{"messages":messages,"form":form})
    def post(self,request,pk,*args,**kwargs):
        form = ArticleTalkForm(request.POST)
        if form.is_valid():
            messages = form.cleaned_data.get('msg')
            article = Article.objects.get(pk=pk)
            article_poster = User.objects.get(pk=article.poster.id)
            msg = self.model.objects.create(msg=messages,msg_from = request.user,msg_to = article_poster,msg_at=article)
            msg.save()
            return redirect("article_talk_suc",pk=pk)

# def article_talk_suc(request):
#     return render(request, 'def_i/article_talk_suc.html')


class ArticleTalkSuc(TemplateView):
    template_name = "article_talk_suc.html"
    def get(self,request,pk):
        return redirect("article_talk",pk=pk)

class ArticlePost(CreateView):
    form_class = ArticlePostForm
    template_name = 'def_i/article_post.html'
    success_url = '../article_feed' #まだ途中なので適当
    def get_initial(self):
        initial = super().get_initial()
        initial['poster']=self.request.user
        print(initial['poster'])
        return initial

class QuestionFeed(ListView):
    model = Question
    context_object_name = "questions"
    template_name = "def_i/question_feed.html"
    paginate_by = 10

    def get_queryset(self):
        questions = Article.objects.order_by('-created_at')
        return questions

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['sort_by_new'] = True
        return context

class QuestionFeedUnanswered(QuestionFeed):
    def get_queryset(self): #queryset=だけでいいことが判明
        articles = Question.objects.filter(if_answered=False)
        return articles

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['sort_by_new'] = False
        return context

class QuestionDetail(DetailView):
    model = Question
    context_object_name = "contents"
    template_name = "def_i/question_detail.html"




# class Login(LoginView):
#     """ログインページ"""
#     form_class = LoginForm
#     template_name = 'def_i/login.html'


# class Logout(LogoutView):
#     """ログアウトページ"""
#     template_name = 'def_i/top.html'
