from django.shortcuts import render,reverse,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,DetailView,FormView,TemplateView,CreateView,UpdateView,DeleteView
from django.views.generic.edit import FormMixin
from .forms import ArticleTalkForm, ArticlePostForm, QuestionPostForm, QuestionTalkForm, MemoForm
from .models import User,Task, Task_Sub, Talk,Like,Article,TalkAtArticle,Question,TalkAtQuestion,Memo
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse,HttpResponse
from django.urls import reverse_lazy
from django.db.models import Q, OuterRef, Subquery
from django.contrib.auth.decorators import login_required


@login_required(login_url ='accounts/login/')
def index(request):
    return render(request,"def_i/index.html")

class ArticleFeed(LoginRequiredMixin,ListView):
    model = Article
    context_object_name = "articles"
    template_name = "def_i/article_feed.html"
    paginate_by = 5

    def get_queryset(self):
        articles = Article.objects.order_by('-created_at')
        for a in articles:
            a.like_count = Like.objects.filter(article = a.pk).count()
            a.save()
        return articles

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['sort_by_new'] = True #新着順かどうか
        context['member'] = User.objects.annotate(latest_post_time=Subquery(
            Article.objects.filter(poster=OuterRef('pk')).values('created_at')[:1],
        )).order_by('-latest_post_time')[:30] #最大表示数を指定
        #以下検索
        query_word =self.request.GET.get('query')
        if query_word:
            articles_list = Article.objects.filter(
                Q(title__icontains=query_word)|Q(poster__username__icontains=query_word)
            )
        else:
            articles_list = Article.objects.order_by('-created_at')
        context['articles'] = articles_list
        return context

class ArticleFeedLike(ArticleFeed):
    def get_queryset(self): #queryset=だけでいいことが判明
        article = Article.objects.all()
        for a in article:
            a.like_count = Like.objects.filter(article = a.pk).count()
        articles = article.order_by('-like_count')
        return articles

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['sort_by_new'] = False
        context['member'] = User.objects.annotate(latest_post_time=Subquery(
            Article.objects.filter(poster=OuterRef('pk')).values('created_at')[:1],
        )).order_by('-latest_post_time')[:30]
        #検索
        query_word =self.request.GET.get('query')
        if query_word:
            objects_list = Article.objects.filter(
                Q(title__icontains=query_word)|Q(poster__username__icontains=query_word)
            )
        else:
            objects_list = Article.objects.order_by('-like_count')
        context['articles'] = objects_list
        return context

class ArticleDetail(LoginRequiredMixin,DetailView): #pk_url_kwargで指定すればkwargsで取得できる
    model = Article
    template_name = "def_i/article_detail.html"
    def get(self,request,pk):
        articles = Article.objects.all()
        liked_list = []
        for a in articles:
            liked = a.like_set.filter(user=request.user)
            if liked.exists():
                liked_list.append(a.pk)
        comments = TalkAtArticle.objects.filter(msg_at=pk).order_by('-time')[:3]
        comments_count = TalkAtArticle.objects.filter(msg_at=pk).count()
        params ={
            'contents':Article.objects.get(pk=pk),
            'liked_list':liked_list,
            'comments_count':comments_count,
            'comments':comments,
        }
        return render(request,self.template_name,params)

class ArticleTalk(LoginRequiredMixin,FormMixin,ListView):
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

class ArticleTalkSuc(LoginRequiredMixin,TemplateView):
    template_name = "article_talk_suc.html"
    def get(self,request,pk):
        return redirect("article_talk",pk=pk)

class ArticlePost(LoginRequiredMixin,CreateView):
    form_class = ArticlePostForm
    template_name = 'def_i/article_post.html'
    success_url = reverse_lazy('article_feed')
    # def get_initial(self): #form_validを使わない場合
    #     initial = super().get_initial()
    #     initial['poster']=self.request.user
    #     return initial

    def form_valid(self,form):
        article = form.save(commit=False)
        article.poster = self.request.user
        article.save()
        messages.success(self.request,'記事を投稿しました．')
        return super().form_valid(form)

    def form_invalid(self,form): #すでにCreateViewでバリデーションされているような気もする
        messages.error(self.request,'記事作成に失敗しました．')
        return super().form_invalid(form)

class ArticleUpdateView(LoginRequiredMixin,UpdateView):
    model = Article
    form_class = ArticlePostForm
    template_name = 'def_i/article_edit.html'

    def get_success_url(self,**kwargs):
        return reverse_lazy('article_detail',kwargs={"pk":self.kwargs['pk']})

    def form_valid(self,form):
        messages.success(self.request,'記事を編集しました．')
        return super().form_valid(form)

    def form_invalid(self,form):
        messages.error(self.request,'記事更新に失敗しました．')
        return super().form_invalid(form)

class ArticleDeleteView(LoginRequiredMixin,DeleteView):
    model = Article
    template_name = 'def_i/article_delete.html'
    success_url = reverse_lazy('article_feed')

    def delete(self,request,*args,**kwargs):
        messages.success(self.request,'記事を削除しました．')
        return super().delete(request,*args,**kwargs)

class QuestionFeed(LoginRequiredMixin,ListView):
    model = Question
    context_object_name = "questions"
    template_name = "def_i/question_feed.html"
    paginate_by = 10
    queryset = Question.objects.order_by('-created_at')

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['sort_by_new'] = True
        context['member'] = User.objects.annotate(latest_post_time=Subquery(
            Article.objects.filter(poster=OuterRef('pk')).values('created_at')[:1],
        )).order_by('-latest_post_time')
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
        context['member'] = User.objects.annotate(latest_post_time=Subquery(
            Article.objects.filter(poster=OuterRef('pk')).values('created_at')[:1],
        )).order_by('-latest_post_time')
        return context

class QuestionDetail(LoginRequiredMixin,DetailView):
    model = Question
    context_object_name = "contents"
    template_name = "def_i/question_detail.html"
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = TalkAtQuestion.objects.filter(msg_at=self.kwargs['pk']).count()
        return context

class QuestionTalk(LoginRequiredMixin,FormMixin,ListView):
    model =TalkAtQuestion
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

class QuestionTalkSuc(LoginRequiredMixin,TemplateView):
    template_name = "question_talk_suc.html"
    def get(self,request,pk):
        return redirect("question_talk",pk=pk)

class QuestionPost(LoginRequiredMixin,CreateView):
    form_class = QuestionPostForm
    template_name = 'def_i/question_post.html'
    success_url = reverse_lazy('question_feed_new')
    def form_valid(self,form):
        question = form.save(commit=False)
        question.poster = self.request.user
        question.save()
        messages.success(self.request,'質問を投稿しました．')
        return super().form_valid(form)

    def form_invalid(self,form): #すでにCreateViewでバリデーションされているような気もする
        messages.error(self.request,'質問作成に失敗しました．')
        return super().form_invalid(form)

class QuestionUpdateView(LoginRequiredMixin,UpdateView):
    model = Question
    form_class = QuestionPostForm
    template_name = 'def_i/question_edit.html'

    def get_success_url(self,**kwargs):
        return reverse_lazy('question_detail',kwargs={"pk":self.kwargs['pk']})

    def form_valid(self,form):
        messages.success(self.request,'質問を編集しました．')
        return super().form_valid(form)

    def form_invalid(self,form):
        messages.error(self.request,'質問更新に失敗しました．')
        return super().form_invalid(form)

class QuestionDeleteView(LoginRequiredMixin,DeleteView):
    model = Question
    template_name = 'def_i/question_delete.html'
    success_url = reverse_lazy('question_feed_new')

    def delete(self,request,*args,**kwargs):
        messages.success(self.request,'質問を削除しました．')
        return super().delete(request,*args,**kwargs)

class BackendTaskList(LoginRequiredMixin,ListView):
    context_object_name = 'task_list'
    queryset = Task.objects.order_by('f_number').prefetch_related('task_sub')
    model = Task
    template_name = "def_i/base-task.html"


    def get_context_data(self , *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['task_sub_list'] = Task_Sub.objects.all()


        return context

class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task_Sub
    context_object_name = 'task_sub'
    fields = ['title','contents',]
    template_name = 'def_i/task_detail.html'


def MemoView(request, pk):
    task_pk = Task_Sub.objects.get(pk=pk)
    memo, created = Memo.objects.get_or_create(relate_user=request.user, relate_task=task_pk)
    if request.method == "POST":
        form = MemoForm(request.POST, instance=memo)
        if form.is_valid():
            form.save()
            return redirect('task_memo', pk=pk)
    else:
        form = MemoForm(instance=memo)

    return render(request, 'def_i/task_memo_form.html', {'form': form, 'memo':memo, 'pk':task_pk })

class TaskQuestion(LoginRequiredMixin, ListView):
    model = Question
    template_name = 'def_i/task_question.html'


class TaskArticle(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'def_i/task_article.html'


class FrontendTaskList(LoginRequiredMixin,ListView):
    model = Task
    template_name = "def_i/base-task.html"

class MessageNotification(LoginRequiredMixin,ListView):
    model = Talk
    template_name = 'def_i/message_notification.html'
    def get(self,request):
        messages = Talk.objects.filter(msg_to=request.user.id).order_by('-time')
        print(messages)
        return render(request,self.template_name,{"messages":messages})

# class LikeView(TemplateView):
#     def post(self,request,pk):
#         article = Article.objects.get(pk=pk)
#         print(article)
#         user = request.user
#         liked = False
#         like = Like.objects.filter(article=article,user=user)
#         if like.exists():
#             like.delete()
#         else:
#             like.create(article=article,user=user)
#             liked = True
#         params={
#             'article_id':article.id,
#             'liked':liked,
#             'count':article.like_set.count(),
#             # 'pk':pk,
#         }
#         if request.is_ajax():
#             return JsonResponse(params)
def LikeView(request,pk):
    if request.method =="GET":
        article = Article.objects.get(pk=pk)
        user = request.user
        liked = False
        like = Like.objects.filter(article=article, user=user)
        if like.exists():
            like.delete()
        else:
            like.create(article=article, user=user)
            liked = True

        params={
            'article_id': article.id,
            'liked': liked,
            'count': article.like_set.count(),
        }

    # if request.is_ajax():
    #     return JsonResponse(params)
    # else:
        return JsonResponse(params)

class UserPageView(LoginRequiredMixin,ListView):
    model = Article
    context_object_name = "articles"
    template_name = 'def_i/user_page.html'
    paginate_by = 5
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(pk=self.kwargs['pk'])
        article_like_count = Article.objects.filter(poster=user).values_list('like_count',flat=True)
        user.like_count = sum(article_like_count)
        user.save()
        context["user_data"] = user
        context["articles_like"] = Article.objects.filter(poster=self.kwargs['pk']).order_by('-like_count')
        return context

    def get_queryset(self,**kwargs):
        articles = Article.objects.filter(poster=self.kwargs['pk']).order_by('-created_at')
        return articles

class MyPageView(LoginRequiredMixin,ListView):
    model = Article
    context_object_name = "articles"
    template_name = 'def_i/my_page.html'
    paginate_by = 5 #標準ではobject_listをうけとる
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user_data"] = User.objects.get(username=user)
        like_article = Like.objects.filter(user=user).values('article') #<QuerySet [{'article': 1}, {'article': 2}]>
        article_list = Article.objects.filter(pk__in = like_article)
        context["articles_like"] = article_list #いいねした記事リスト
        # context["articles"] = Article.objects.filter(poster=user)
        return context

    def get_queryset(self,**kwargs):
        articles = Article.objects.filter(poster=self.request.user).order_by('-created_at')
        return articles
