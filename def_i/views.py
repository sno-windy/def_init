import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator

from django.db.models import F, OuterRef, Q, Subquery
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, TemplateView, UpdateView)
from django.views.generic import ListView,DetailView,FormView,TemplateView,CreateView,UpdateView,DeleteView
from django.views.generic.edit import FormMixin

from .forms import *
from .index_info import GetIndexInfo
from .models import *


#反省 Controllerに処理を書きすぎない

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "def_i/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        info = GetIndexInfo(self.request.user)

        context["ranking"] = info.get_ranking()
        context["learning_lesson"] = info.learning_lesson
        context["progress"] = info.get_progress(self.request.user)
        context["questions"] = info.get_related_questions()
        context["articles"] = info.get_related_articles()

        context["colleagues"] = info.get_colleagues(self.request.user)

        new_likes, article_talk, question_talk = info.get_notification(self.request.user)
        context["new_likes"] = new_likes
        context["article_talk"] = article_talk
        context["question_talk"] = question_talk
        return context


class ArticleFeed(LoginRequiredMixin,FormMixin,ListView):
    model = Article
    form_class = ArticleSearchForm
    context_object_name = "articles"
    template_name = "def_i/article_feed.html"
    paginate_by = 5

    def get_initial(self):
        return self.request.GET #検索の値の保持.copy()

    def get_queryset(self):
        articles = Article.objects.all()
        order_by = self.request.GET.get('orderby')

        if order_by == 'new':
            articles = Article.objects.order_by('-created_at')

        elif order_by == 'like':
            articles = articles.order_by('-like_count','-created_at')

        if (query_word := self.request.GET.get('keyword')): #代入式
            articles = articles.filter(
                Q(title__icontains=query_word)|Q(poster__username__icontains=query_word)
            )

        return articles

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        # context['sort_by_new'] = True #新着順かどうか=>クエリパラメーターで扱う
        context['orderby'] = self.request.GET.get('orderby')

        context['member'] = User.objects.annotate(
            latest_post_time=Subquery(
            Article.objects.filter(poster=OuterRef('pk')).values('created_at')[:1],
        )).order_by('-latest_post_time')[:30] #最大表示数を指定

        return context


class ArticleDetail(LoginRequiredMixin,DetailView): #pk_url_kwargで指定すればkwargsで取得できる
    model = Article
    template_name = "def_i/article_detail.html"
    def get(self,request,pk):
        articles = Article.objects.all()
        #Userがlikeしてるかどうかの判別
        liked_set = Like.objects.filter(user=request.user).values_list('article',flat=True)
        cm = TalkAtArticle.objects.filter(msg_at=pk)
        comments = cm.order_by('-time')[:3]
        comments_count = cm.count() #lenにしてQuerysetが走っている回数を数える．
        params ={
            'contents':Article.objects.get(pk=pk),
            'liked_set':liked_set,
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
        return render(request,self.template_name,
            {
                "messages":messages,
                "form":form,
                'pk':pk
            })

    def post(self,request,pk,*args,**kwargs):
        form = ArticleTalkForm(request.POST)
        if form.is_valid():
            messages = form.cleaned_data.get('msg')
            article = Article.objects.get(pk=pk)
            article_poster = User.objects.get(pk=article.poster.id)
            msg = self.model.objects.create(msg=messages,msg_from = request.user,msg_to = article_poster,msg_at=article)
            return redirect("article_talk_suc",pk=pk)

#投稿完了画面を作ったが，すぐ元の画面に遷移するので活用できていない
class ArticleTalkSuc(LoginRequiredMixin,TemplateView):
    template_name = "article_talk_suc.html"
    def get(self,request,pk):
        return redirect("article_talk",pk=pk)


class ArticlePost(LoginRequiredMixin,CreateView):
    form_class = ArticlePostForm
    template_name = 'def_i/article_post.html'
    success_url = reverse_lazy('article_feed')
    #form_valid()を使わない場合，get_initial()で初期値をユーザーにすればよい

    def form_valid(self,form):
        article = form.save(commit=False)
        article.poster = self.request.user
        course,_ = Course.objects.get_or_create(title='public')
        article_at,_ = Lesson.objects.get_or_create(title='public',contents='',course=course)
        article.article_at = article_at
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

    def get_queryset(self):
        order_by = self.request.GET.get('orderby')
        questions = Question.objects.all()

        if order_by == 'new':
            questions = questions.order_by('-created_at')

        elif order_by == 'unanswered':
            questions = questions.filter(if_answered=False)

        return questions

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['orderby'] = self.request.GET.get('orderby')
        context['member'] = User.objects.annotate(
            latest_post_time=Subquery(
                Article.objects.filter(
                    poster=OuterRef('pk')).values('created_at')[:1],
                )
        ).order_by('-latest_post_time')
        return context


class QuestionDetail(LoginRequiredMixin,DetailView):
    model = Question
    context_object_name = "contents"
    template_name = "def_i/question_detail.html"

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        comments = TalkAtQuestion.objects.filter(msg_at=self.kwargs['pk'])
        context['comments_count'] = comments.count()
        context['comments'] = comments.order_by('-time')[:3]
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
            if not question.if_answered: #コメントの時にブール値を編集する
                question.if_answered = True
                question.save()

            return redirect("question_talk_suc",pk=pk)


class QuestionTalkSuc(LoginRequiredMixin,TemplateView):
    template_name = "question_talk_suc.html"
    def get(self,request,pk):
        return redirect("question_talk",pk=pk)


class QuestionPost(LoginRequiredMixin,CreateView):
    form_class = QuestionPostForm
    template_name = 'def_i/question_post.html'
    success_url = reverse_lazy('question_feed')

    def form_valid(self,form):
        question = form.save(commit=False)
        question.poster = self.request.user
        course,_ = Course.objects.get_or_create(title='public')
        question_at,_ = Lesson.objects.get_or_create(title='public',contents='',course=course)
        question.question_at = question_at
        question.save()
        #push通知
        question.browser_push(self.request)
        question.notify_new_question()

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

class TaskQuestionPost(LoginRequiredMixin,CreateView):
    form_class = QuestionPostForm
    template_name = 'def_i/question_post.html'

    def form_valid(self, form, **kwargs):
        pk = self.kwargs['pk']
        question_at = Lesson.objects.get(pk=pk)
        question = form.save(commit=False)
        question.poster = self.request.user
        question.question_at = question_at
        question.save()
        messages.success(self.request,'質問を投稿しました．')
        return super().form_valid(form)

    def form_invalid(self,form): #すでにCreateViewでバリデーションされているような気もする
        messages.error(self.request,'質問作成に失敗しました．')
        return super().form_invalid(form)

    def get_success_url(self,**kwargs):
        return reverse_lazy('task_question',kwargs={"pk":self.kwargs['pk']})

class TaskArticlePost(LoginRequiredMixin, CreateView):
    form_class = ArticlePostForm
    template_name = 'def_i/article_post.html'

    def form_valid(self, form, **kwargs):
        pk = self.kwargs['pk']
        article_at = Lesson.objects.get(pk=pk)
        article = form.save(commit=False)
        article.poster = self.request.user
        article.article_at = article_at
        article.save()
        messages.success(self.request,'記事を投稿しました．')
        return super().form_valid(form)

    def form_invalid(self,form): #すでにCreateViewでバリデーションされているような気もする
        messages.error(self.request,'記事作成に失敗しました．')
        return super().form_invalid(form)

    def get_success_url(self,**kwargs):
        return reverse_lazy('task_article',kwargs={"pk":self.kwargs['pk']})


def course(request):
    return render(request, "def_i/course.html")


class BackendTaskList(LoginRequiredMixin,ListView):
    context_object_name = 'course_list'
    queryset = Course.objects.order_by('course_num').prefetch_related('lesson') #ここがmodelsのrelatedと繋がってるのはわかったけどなんでこの名前がlessonじゃないとだめなのかがわからん
    model = Course
    template_name = "def_i/base-task.html"

    def get_context_data(self , *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['lesson_list'] = Lesson.objects.all()
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Lesson
    context_object_name = 'lesson'
    fields = ['title','contents',]
    template_name = 'def_i/task_detail.html'


class TaskQuestion(LoginRequiredMixin, ListView):
    model = Question
    template_name = 'def_i/task_question.html'

    def get_queryset(self):
        order_by = self.request.GET.get('orderby')
        lesson = Lesson.objects.get(pk=self.kwargs['pk'])
        questions = Question.objects.filter(question_at=lesson)
        if order_by == 'new':
            questions = questions.order_by('-created_at')

        elif order_by == 'unanswered':
            questions = questions.filter(if_answered=False)

        return questions

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['orderby'] = self.request.GET.get('orderby')
        user = self.request.user
        lesson = Lesson.objects.get(pk=self.kwargs['pk'])
        my_question_list = Question.objects.filter(poster=user).order_by('-created_at')
        context['lesson'] = lesson
        context['my_question_list'] = my_question_list

        return context


class TaskArticle(LoginRequiredMixin, ListView):
    model = Article
    template_name = "def_i/task_article.html"
    paginate_by = 5

    def get_queryset(self):
        order_by = self.request.GET.get('orderby')
        questions = Question.objects.all()
        lesson = Lesson.objects.get(pk=self.kwargs['pk'])
        articles = Article.objects.filter(article_at=lesson)
        if order_by == 'new':
            articles = articles.order_by('-created_at')

        elif order_by == 'like':
            articles = articles.order_by('-like_count','-created_at')

        if (query_word := self.request.GET.get('keyword')): #代入式
            articles = articles.filter(
                Q(title__icontains=query_word)|Q(poster__username__icontains=query_word)
            )

        return articles

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['orderby'] = self.request.GET.get('orderby')
        user = self.request.user
        pk = self.kwargs['pk']
        lesson = Lesson.objects.get(pk=pk)
        my_article_list = Article.objects.filter(article_at=lesson, poster=user).order_by('-created_at')
        context['lesson'] = lesson
        context['my_article_list'] = my_article_list

        return context


class FrontendTaskList(LoginRequiredMixin,ListView):
    model = Course
    template_name = "def_i/base-task.html"


@login_required(login_url ='accounts/login/')
def note_list(request):
    return render(request,"def_i/note_list.html")


class MessageNotification(LoginRequiredMixin,TemplateView):
    template_name = 'def_i/message_notification.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    ####記事と質問のTalkを回収して，Unionさせている．Unionによって消えてしまう情報(Title,pk)をannotateしている
        msg_article = TalkAtArticle.objects.annotate(
            msg_at_title=Subquery(
                Article.objects.filter(pk=OuterRef('msg_at')).values('title')[:1]
            ),
            msg_at_pk=Subquery(
                Article.objects.filter(pk=OuterRef('msg_at')).values('pk')[:1]
            )
        ).filter(msg_to=self.request.user.id)

        msg_question = TalkAtQuestion.objects.annotate(
            msg_at_title=Subquery(
                Question.objects.filter(pk=OuterRef('msg_at')).values('title')[:1]
            ),
            msg_at_pk=Subquery(
                Question.objects.filter(pk=OuterRef('msg_at')).values('pk')[:1]
            )
        ).filter(msg_to=self.request.user.id)
        msg_union = msg_article.union(msg_question).order_by('-time')
        context["messages"] = msg_union
        return context


def LikeView(request,pk):
    if request.method =="GET":
        article = Article.objects.get(pk=pk) #filterでないとF&updateが使えにゃい
        article_poster = article.poster
        user = request.user
        is_liked = False
        like = Like.objects.filter(article=article, user=user)

        if like.exists():
            like.delete()
            article.like_count=F('like_count')-1
            article_poster.like_count=F('like_count')-1

        else:
            like.create(article=article, user=user)
            article.like_count=F('like_count')+1
            article_poster.like_count=F('like_count')+1
            is_liked = True

        article.save()
        article_poster.save()
        params={
            'article_id': article.id,
            'liked': is_liked,
            'count': article.like_set.count(),
        }

        return JsonResponse(params)

class UserPageView(LoginRequiredMixin,ListView):
    model = Article
    context_object_name = "articles"
    template_name = 'def_i/user_page.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(pk=self.kwargs['pk'])
        context["user_data"] = user
        context["articles_like"] = Article.objects.filter(poster=self.kwargs['pk']).order_by('-like_count')[:5]
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
        info = GetIndexInfo(user)
        # like_article = Like.objects.filter(user=user).values('article') #<QuerySet [{'article': 1}, {'article': 2}]>
        # article_list = Article.objects.filter(pk__in = like_article).order_by('-created_at')
        article_list = Article.objects.filter(like__user=user) #逆参照を使いましょう．
        question_list = Question.objects.filter(poster=user).order_by('-created_at')
        learning_lesson = info.learning_lesson
        context["learning_lesson"] = learning_lesson
        context["articles_like"] = article_list #いいねした記事リスト
        context["questions"] = question_list
        context["learning_course"] = Course.objects.get(lesson=learning_lesson)
        return context

    def get_queryset(self,**kwargs):
        articles = Article.objects.filter(poster=self.request.user).order_by('-created_at')
        return articles


@csrf_exempt
def new_line_friend(request):
    if request.method == 'POST':
        request_json = json.loads(request.body.decode('utf-8'))
        events = request_json['events']
        if events:
            line_user_id = events[0]['source']['userId']

            if events[0]['type'] == 'follow':
                a = LineFriend.objects.create(line_user_id=line_user_id)
                print(a)

    return HttpResponse()
