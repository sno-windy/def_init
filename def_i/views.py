import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import F, OuterRef, Q, Subquery
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, TemplateView, UpdateView)
from django.views.generic import ListView,DetailView,FormView,TemplateView,CreateView,UpdateView,DeleteView
from django.views.generic.edit import FormMixin
from linebot import LineBotApi, WebhookHandler
from linebot.models import TemplateSendMessage, TextSendMessage

from .forms import *
from .index_info import GetIndexInfo
from .models import *
from .line import *


#反省 Controllerに処理を書きすぎない

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "def_i/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        info = GetIndexInfo(self.request.user)

        context["ranking"] = info.get_ranking()
        context["learning_lesson"] = info.learning_lesson
        all_progress,each_progress = info.get_progress(self.request.user)
        context["all_progress"] = all_progress
        context["each_progress"] = each_progress
        context["questions"] = info.get_related_questions()
        context["articles"] = info.get_related_articles()

        context["colleagues"] = info.get_colleagues(self.request.user)

        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(self.request.user)
        context["new_bookmarks"] = new_bookmarks
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
        articles = Article.objects.filter(Q(poster=self.request.user)|Q(is_published=True)).order_by('-created_at')
        order_by = self.request.GET.get('orderby')

        if order_by == 'new':
            articles = Article.objects.filter(is_published=True).order_by('-created_at')

        elif order_by == 'like':
            articles = Article.objects.filter(is_published=True).order_by('-like_count','-created_at')

        elif order_by == 'mynote':
            articles = articles.filter(poster=self.request.user).order_by('-created_at')

        if (query_word := self.request.GET.get('keyword')): #代入式
            articles = articles.filter(
                Q(title__icontains=query_word)|Q(poster__username__icontains=query_word)
            ).filter(is_published=True).order_by('-created_at')

        return articles

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        # context['sort_by_new'] = True #新着順かどうか=>クエリパラメーターで扱う
        context['orderby'] = self.request.GET.get('orderby')

        context['member'] = User.objects.annotate(
            latest_post_time=Subquery(
            Article.objects.filter(poster=OuterRef('pk'), is_published=True).values('created_at')[:1],
        )).order_by('-latest_post_time')[:30] #最大表示数を指定

        return context


class ArticleDetail(LoginRequiredMixin, FormMixin, ListView):
    model =TalkAtArticle
    # context_object_name = "messages"
    form_class = ArticleTalkForm #いらんかも
    template_name = 'def_i/article_detail.html'

    def get(self, request, pk):
        form = ArticleTalkForm()
        article = Article.objects.get(pk=pk)
        liked_set = Like.objects.filter(user=request.user).values_list('article',flat=True)

        comments = TalkAtArticle.objects.filter(msg_at=article).order_by('-time')[:3]
        comments_count = comments.count() #lenにしてQuerysetが走っている回数を数える．

        related_articles = Article.objects.exclude(pk=article.pk).filter(course=article.course).filter(Q(is_published=True)|Q(poster=request.user)).order_by('-created_at')[:5]
        return render(request,self.template_name,
            {
                "form":form,
                'contents': article,
                'liked_set':liked_set,
                'comments_count':comments_count,
                'comments':comments,
                'related_articles': related_articles,
            })

    def post(self, request, pk, *args, **kwargs):
        form = ArticleTalkForm(request.POST)
        if form.is_valid():
            messages = form.cleaned_data.get('msg')
            article = Article.objects.get(pk=pk)
            article_poster = User.objects.get(pk=article.poster.id)
            msg = self.model.objects.create(msg=messages, msg_from=request.user, msg_to=article_poster, msg_at=article)
            msg.notify_new_comment()
            return redirect("article_detail", pk=pk)


class ArticlePost(LoginRequiredMixin,CreateView):
    form_class = ArticlePostForm
    template_name = 'def_i/article_post.html'
    success_url = reverse_lazy('article_post')
    #form_valid()を使わない場合，get_initial()で初期値をユーザーにすればよい

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course_dict"] = pass_courses
        context["lesson_dict"] = pass_lessons
        return context

    def form_valid(self,form):
        article = form.save(commit=False)
        article.poster = self.request.user
        course,_ = Course.objects.get_or_create(title='public')
        article_at,_ = Lesson.objects.get_or_create(title='public',contents='',course=course)
        article.lesson = article_at
        article.save()
        messages.success(self.request,'ノートを保存しました．')
        return super().form_valid(form)

    def form_invalid(self,form): #すでにCreateViewでバリデーションされているような気もする
        messages.error(self.request,'ノート保存に失敗しました．')
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


class QuestionFeed(LoginRequiredMixin, FormMixin, ListView):
    model = Question
    form_class = QuestionSearchForm
    context_object_name = "questions"
    template_name = "def_i/question_feed.html"
    paginate_by = 10

    def get_queryset(self):
        order_by = self.request.GET.get('orderby')
        questions = Question.objects.all().order_by('-created_at')

        if order_by == 'new':
            questions = questions.order_by('-created_at')

        elif order_by == 'unanswered':
            questions = questions.filter(if_answered=False).order_by('created_at')

        elif order_by == 'myquestion':
            questions = questions.filter(poster=self.request.user).order_by('-created_at')

        if (query_word := self.request.GET.get('keyword')):
            questions = questions.filter(
                Q(title__icontains=query_word)|Q(poster__username__icontains=query_word)
            ).order_by('-created_at')

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


class QuestionDetail(LoginRequiredMixin, FormMixin, ListView):
    model =TalkAtQuestion
    form_class = QuestionTalkForm
    template_name = 'def_i/question_detail.html'

    def get(self, request, pk):
        form = QuestionTalkForm()
        question = Question.objects.get(pk=pk)
        bookmark_set = BookMark.objects.filter(question=question, user=request.user).values_list('question', flat=True)
        comments = question.talkatquestion_set.all().order_by('-time')

        related_questions = Question.objects.filter(course=question.course).exclude(pk=question.pk).order_by('-created_at')[:5]

        return render(request, self.template_name, {
            "contents": question,
            "bookmark_set": bookmark_set,
            "comments": comments,
            "form": form,
            "related_questions": related_questions,
        })

    def post(self, request,pk, *args, **kwargs):
        form = QuestionTalkForm(request.POST)
        if form.is_valid():
            messages = form.cleaned_data.get('msg')
            question = Question.objects.select_related('poster').get(pk=pk)
            question_poster = question.poster
            msg = self.model.objects.create(msg=messages, msg_from=request.user, msg_to=question_poster, msg_at=question)
            msg.save()
            print('saved')
            msg.notify_new_comment()
            if not question.if_answered: #コメントの時にブール値を編集する
                question.if_answered = True
                question.save()

            return redirect("question_talk_suc",pk=pk)

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        comments = TalkAtQuestion.objects.filter(msg_at=self.kwargs['pk'])
        context['comments_count'] = comments.count()
        context['comments'] = comments.order_by('-time')[:3]
        return context


def BookMarkView(request, pk):
    if request.method =="GET":
        question = Question.objects.get(pk=pk)
        question_poster = question.poster
        user = request.user
        is_bookmarked = False
        bookmark = BookMark.objects.filter(question=question, user=user)

        if bookmark.exists():
            bookmark.delete()
            question.bookmark_count=F('bookmark_count')-1
            # question_poster.bookmark_count=F('bookmark_count')-1

        else:
            BookMark.objects.create(question=question, user=user)
            question.bookmark_count=F('bookmark_count')+1
            # question_poster.bookmark_count=F('bookmark_count')+1
            is_bookmarked = True

        question.save()
        # question_poster.save()
        params={
            'question_id': question.id,
            'bookmarked': is_bookmarked,
            'bookmark_count': question.bookmark_set.count(),
        }

        return JsonResponse(params)

class QuestionTalkSuc(LoginRequiredMixin,TemplateView):
    template_name = "question_talk_suc.html"
    def get(self,request,pk):
        return redirect("question_detail",pk=pk)


class QuestionPost(LoginRequiredMixin,CreateView):
    form_class = QuestionPostForm
    template_name = 'def_i/question_post.html'
    success_url = reverse_lazy('question_post')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course_dict"] = pass_courses
        context["lesson_dict"] = pass_lessons
        return context

    def form_valid(self,form):
        question = form.save(commit=False)
        question.poster = self.request.user
        course,_ = Course.objects.get_or_create(title='public')
        question_at,_ = Lesson.objects.get_or_create(title='public',contents='',course=course)
        question.lesson = question_at
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
        if uploaded := self.request.POST.get('question_image_1'):
            print('file')
            print(uploaded)
        else:
            print('no file')
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


class TaskQuestionPost(LoginRequiredMixin, CreateView):
    form_class = QuestionPostForm
    template_name = 'def_i/task_question_post.html'

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        question_at = Lesson.objects.select_related("course__category").get(pk=self.kwargs['pk'])
        form_kwargs['initial'] = {
            "lesson": question_at,
            "course": question_at.course,
            "category": question_at.course.category,
        }
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course_dict"] = pass_courses
        context["lesson_dict"] = pass_lessons
        context["pk"] = self.kwargs["pk"]
        return context

    def form_valid(self, form, **kwargs):
        pk = self.kwargs['pk']
        question_at = Lesson.objects.get(pk=pk)
        question = form.save(commit=False)
        question.poster = self.request.user
        question.lesson = question_at
        question.save()
        question.notify_new_question()
        messages.success(self.request,'質問を投稿しました．')
        return super().form_valid(form)

    def form_invalid(self,form): #すでにCreateViewでバリデーションされているような気もする
        messages.error(self.request,'質問作成に失敗しました．')
        return super().form_invalid(form)

    def get_success_url(self,**kwargs):
        return reverse_lazy('task_question_post',kwargs={"pk":self.kwargs['pk']})


class TaskArticlePost(LoginRequiredMixin, CreateView):
    form_class = ArticlePostForm
    template_name = 'def_i/task_article_post.html'

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        article_at = Lesson.objects.select_related("course__category").get(pk=self.kwargs['pk'])
        form_kwargs['initial'] = {
            "lesson": article_at,
            "course": article_at.course,
            "category": article_at.course.category,
        }
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course_dict"] = pass_courses()
        context["lesson_dict"] = pass_lessons()
        context["pk"] = self.kwargs["pk"]
        return context

    def form_valid(self, form, **kwargs):
        pk = self.kwargs['pk']
        article_at = Lesson.objects.get(pk=pk)
        article = form.save(commit=False)
        article.poster = self.request.user
        article.lesson = article_at
        article.save()
        messages.success(self.request,'ノートを保存しました．')
        return super().form_valid(form)

    def form_invalid(self,form): #すでにCreateViewでバリデーションされているような気もする
        messages.error(self.request,'ノート保存に失敗しました．')
        return super().form_invalid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('task_article_post',kwargs={"pk":self.kwargs['pk']})


def pass_courses():
    categories = Category.objects.all().prefetch_related("course_set")
    course_dict = {}
    for category in categories:
        course_dict[category.pk] = []
        for category_course in category.course_set.all():
            course_dict[category.pk].append({
                "pk": category_course.pk,
                "title": category_course.title,
            })

    course_dict_json = json.dumps(course_dict, ensure_ascii=False)
    return course_dict_json

def pass_lessons():
    courses = Course.objects.all().prefetch_related("lessons")
    lesson_dict = {}
    for course in courses:
        lesson_dict[course.pk] = []
        for lesson in course.lessons.all():
            lesson_dict[course.pk].append({
                "pk": lesson.pk,
                "title": lesson.title,
            })
    lesson_dict_json = json.dumps(lesson_dict, ensure_ascii=False)
    return lesson_dict_json

def course(request):
    if request.method == 'GET':
        info = GetIndexInfo(request.user)
        _,progress = info.get_progress(request.user)
        params = {
            "progress":progress,
        }
    return render(request, "def_i/course.html",params)


class CourseList(LoginRequiredMixin,ListView):
    context_object_name = 'course_and_progress'
    model = Course
    template_name = "def_i/base-task.html"

    def get_queryset(self,**kwargs):
        course_list = Course.objects.filter(category__title=self.kwargs['category']).order_by('course_num').prefetch_related('lessons')
        progress_percent_list = []
        for course in course_list:
            lessons = course.lessons.all()
            lesson_count = lessons.count()
            cleared_lesson_count = ClearedLesson.objects.filter(lesson__in = lessons).count()
            if lessons:
                progress_percent = round(cleared_lesson_count * 100 / lesson_count,1)
                progress_percent_list.append(progress_percent)
        course_and_progress = [[crs,per] for crs,per in zip(course_list,progress_percent_list)]
        print(course_and_progress)
        return course_and_progress



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
        questions = Question.objects.filter(lesson=lesson)
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
        articles = Article.objects.filter(lesson=lesson).filter(Q(poster=self.request.user)|Q(is_published=True))
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
        my_article_list = Article.objects.filter(lesson=lesson, poster=user).order_by('-created_at')
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

# class UserPageView(LoginRequiredMixin,ListView):
#     model = Article
#     context_object_name = "articles"
#     template_name = 'def_i/user_page.html'
#     paginate_by = 5

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user = User.objects.get(pk=self.kwargs['pk'])
#         context["user_data"] = user
#         context["articles_like"] = Article.objects.filter(poster=self.kwargs['pk']).order_by('-like_count')[:5]
#         return context

#     def get_queryset(self,**kwargs):
#         articles = Article.objects.filter(poster=self.kwargs['pk']).order_by('-created_at')
#         return articles

# class MyPageView(LoginRequiredMixin,ListView):
#     model = Article
#     context_object_name = "articles"
#     template_name = 'def_i/my_page.html'
#     paginate_by = 5 #標準ではobject_listをうけとる

#     def get_context_data(self,**kwargs):
#         context = super().get_context_data(**kwargs)
#         user = self.request.user
#         info = GetIndexInfo(user)
#         # like_article = Like.objects.filter(user=user).values('article') #<QuerySet [{'article': 1}, {'article': 2}]>
#         # article_list = Article.objects.filter(pk__in = like_article).order_by('-created_at')
#         article_list = Article.objects.filter(like__user=user) #逆参照を使いましょう．
#         question_list = Question.objects.filter(poster=user).order_by('-created_at')
#         learning_lesson = info.learning_lesson
#         context["learning_lesson"] = learning_lesson
#         context["articles_like"] = article_list #いいねした記事リスト
#         context["questions"] = question_list
#         # context["learning_course"] = Course.objects.get(lesson=learning_lesson)
#         return context

#     def get_queryset(self,**kwargs):
#         articles = Article.objects.filter(poster=self.request.user).order_by('-created_at')
#         return articles

def mypage_view(request):
    user = request.user
    orderby = request.GET.get('orderby')
    question = Question.objects.order_by('created_at')
    if orderby == 'like':
        question_like = question.filter(bookmark__user=user)
        paginator = Paginator(question_like,5)
    else:
        question = question.filter(poster=user)
        paginator = Paginator(question,5)

    page = request.GET.get('q_page')

    try:
        question = paginator.page(page)
    except PageNotAnInteger:
        question = paginator.page(1)
    except EmptyPage:
        question = paginator.page(paginator.num_pages)


    article = Article.objects.order_by('-created_at')
    if orderby == 'like':
        article_like = article.filter(like__user=user)
        paginator = Paginator(article_like,5)
    else:
        article = article.filter(poster=user)
        paginator = Paginator(article, 5)

    page = request.GET.get('a_page')

    try:
        article = paginator.page(page)
    except PageNotAnInteger:
        article = paginator.page(1)
    except EmptyPage:
        article = paginator.page(paginator.num_pages)

    params = {
        'question':question,
        'article':article,
    }
    return render(request, 'def_i/my_page.html', params)


def userpage_view(request,pk):
    user = User.objects.get(pk=pk)
    question = Question.objects.order_by('created_at').filter(poster=user)

    paginator = Paginator(question,5)
    page = request.GET.get('q_page')

    try:
        question = paginator.page(page)
    except PageNotAnInteger:
        question = paginator.page(1)
    except EmptyPage:
        question = paginator.page(paginator.num_pages)


    article = Article.objects.order_by('-created_at').filter(poster=user)

    paginator = Paginator(article, 5)
    page = request.GET.get('a_page')

    try:
        article = paginator.page(page)
    except PageNotAnInteger:
        article = paginator.page(1)
    except EmptyPage:
        article = paginator.page(paginator.num_pages)

    params = {
        'question':question,
        'article':article,
        'user_data':user
    }
    return render(request, 'def_i/user_page.html', params)



@csrf_exempt
def callback(request):
    return handle_callback(request)
