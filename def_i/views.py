from django.shortcuts import render,reverse,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,DetailView,FormView,TemplateView,CreateView
from django.views.generic.edit import FormMixin
from .forms import ArticleTalkForm, ArticlePostForm, QuestionPostForm, QuestionTalkForm
from .models import User,Task,Talk,Article,TalkAtArticle,Question,TalkAtQuestion

from django.core.exceptions import ObjectDoesNotExist

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
        return render(request,self.template_name,{"messages":messages,"form":form,'pk':pk})
    def post(self,request,pk,*args,**kwargs):
        form = ArticleTalkForm(request.POST)
        if form.is_valid():
            messages = form.cleaned_data.get('msg')
            article = Article.objects.get(pk=pk)
            article_poster = User.objects.get(pk=article.poster.id)
            msg = self.model.objects.create(msg=messages,msg_from = request.user,msg_to = article_poster,msg_at=article)
            msg.save()
            return redirect("article_talk_suc",pk=pk)

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
        return initial

class QuestionFeed(ListView):
    model = Question
    context_object_name = "questions"
    template_name = "def_i/question_feed.html"
    # paginate_by = 10
    queryset = Question.objects.order_by('-created_at')

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['sort_by_new'] = True
        return context

class QuestionFeedUnanswered(QuestionFeed):
    def get_queryset(self):
        question = Question.objects.all()
        for q in question:
            talk = TalkAtQuestion.objects.filter(msg_at=q)
            if len(talk) == 0:
                q.if_answered = False
                q.save()
            else:
                q.if_answered = True
                q.save()

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

class QuestionTalk(FormMixin,ListView):
    model =TalkAtQuestion
    context_object_name = "messages"
    form_class = QuestionTalkForm #いらんかも
    template_name = 'def_i/question_talk.html'
    def get(self,request,pk):
        form = QuestionTalkForm()
        question = Question.objects.get(pk=pk)
        messages = TalkAtQuestion.objects.filter(msg_at=question).order_by('time')
        return render(request,self.template_name,{"messages":messages,"form":form,'pk':pk})
    def post(self,request,pk,*args,**kwargs):
        form = QuestionTalkForm(request.POST)
        if form.is_valid():
            messages = form.cleaned_data.get('msg')
            question = Question.objects.get(pk=pk)
            question_poster = User.objects.get(pk=question.poster.id)
            msg = self.model.objects.create(msg=messages,msg_from = request.user,msg_to = question_poster,msg_at=question)
            msg.save()
            return redirect("question_talk_suc",pk=pk)

class QuestionTalkSuc(TemplateView):
    template_name = "question_talk_suc.html"
    def get(self,request,pk):
        return redirect("question_talk",pk=pk)

class QuestionPost(CreateView):
    form_class = QuestionPostForm
    template_name = 'def_i/question_post.html'
    success_url = '../question_feed_new/' #まだ途中なので適当
    def get_initial(self):
        initial = super().get_initial()
        initial['poster']=self.request.user
        return initial

class BackendTaskList(ListView):
    model = Task
    template_name = "def_i/base-task.html"

class FrontendTaskList(ListView):
    model = Task
    template_name = "def_i/base-task.html"

# class MessageNotification(ListView):
#     model = Talk
#     template_name = 'def_i/message_notification.html'
#     def get(self,request):
#         messages = Talk.objects.filter(msg_to=request.user.id).order_by('time')
#         return redirect(request,'def_i/message_notification.html',{"messages":messages,})
