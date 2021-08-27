import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import F, OuterRef, Q, Subquery
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin, ModelFormMixin
from .forms import *
from .index_info import GetIndexInfo
from .models import *
from .line import *


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "def_i/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            studying = StudyingCategory.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            studying = None

        context["studying"] = studying
        info = GetIndexInfo(self.request.user)

        context["ranking"], context["user_ranking"] = info.get_ranking(self.request.user)
        context["learning_lesson"] = info.learning_lesson
        all_progress, each_progress = info.get_progress(self.request.user)
        context["all_progress"] = all_progress
        context["each_progress"] = each_progress
        context["question"] = info.get_related_questions()
        context["article"] = info.get_related_articles()

        context["colleagues"] = info.get_colleagues(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(self.request.user)
        context["new_bookmarks"] = new_bookmarks
        context["new_likes"] = new_likes
        context["article_talk"] = article_talk
        context["question_talk"] = question_talk
        return context


class ArticleFeed(LoginRequiredMixin, FormMixin, ListView):
    model = Article
    form_class = ArticleSearchForm
    context_object_name = "articles"
    template_name = "def_i/article_feed.html"
    paginate_by = 5
    page_kwarg = "a_page"

    def get_initial(self):
        return self.request.GET  # 検索の値の保持.copy()

    def get_queryset(self):
        articles = Article.objects.order_by('-created_at')
        order_by = self.request.GET.get('orderby')

        if order_by == 'like':
            articles = Article.objects.filter(
                is_published=True).order_by('-like_count', '-created_at')

        elif order_by == 'mynote':
            articles = articles.filter(
                poster=self.request.user).order_by('-created_at')

        else:  # new など
            articles = Article.objects.filter(
                is_published=True).order_by('-created_at')

        if (query_word := self.request.GET.get('keyword')):  # 代入式
            articles = articles.filter(
                Q(title__icontains=query_word) | Q(poster__username__icontains=query_word)
            ).filter(is_published=True).order_by('-created_at')

        return articles

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orderby'] = self.request.GET.get('orderby')
        context["article"] = context["page_obj"]

        context['member'] = User.objects.annotate(
            latest_post_time=Subquery(
                Article.objects.filter(poster=OuterRef(
                    'pk'), is_published=True).values('created_at')[:1],
            )).order_by('-latest_post_time')[:30]  # 最大表示数を指定
        info = GetIndexInfo(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            self.request.user)
        context["new_bookmarks"] = new_bookmarks
        context["new_likes"] = new_likes
        context["article_talk"] = article_talk
        context["question_talk"] = question_talk

        return context


class ArticleDetail(LoginRequiredMixin, ModelFormMixin, ListView):
    model = TalkAtArticle
    template_name = 'def_i/article_detail.html'

    def get(self, request, pk):
        article = Article.objects.get(pk=pk)
        liked_set = Like.objects.filter(
            user=request.user).values_list('article', flat=True)

        comments = TalkAtArticle.objects.filter(
            msg_at=article).order_by('time')
        comments_count = comments.count()  # lenにしてQuerysetが走っている回数を数える．

        related_articles = Article.objects.exclude(pk=article.pk).filter(
            course=article.course).filter(is_published=True).order_by('-created_at')[:5]
        info = GetIndexInfo(request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            request.user)

        return render(request, self.template_name,
            {
                'contents': article,
                'liked_set': liked_set,
                'comments_count': comments_count,
                'comments': comments,
                'related_articles': related_articles,
                'comment_form': ArticleTalkForm(),

                'new_likes': new_likes,
                'new_bookmarks': new_bookmarks,
                'article_talk': article_talk,
                'question_talk': question_talk,
            }
        )

    def post(self, request, pk):
        if 'comment_form' in request.POST:
            comment_form = ArticleTalkForm(request.POST)
            if comment_form.is_valid():
                messages = comment_form.cleaned_data.get('msg')
                article = Article.objects.get(pk=pk)
                article_poster = User.objects.get(pk=article.poster.id)
                msg = self.model.objects.create(
                    msg=messages, msg_from=request.user, msg_to=article_poster, msg_at=article)
                msg.notify_new_comment()
                return redirect("article_detail", pk=pk)

        elif 'publish_form' in request.POST:
            article = Article.objects.get(pk=pk)
            publish_form = ArticlePublishForm(request.POST, instance=article)
            publish = request.POST.get("publish")
            if publish == "on":
                publish = True
            else:
                publish = False
            if publish_form.is_valid():
                article.is_published = publish
                article.save()
            return redirect("article_detail", pk=pk)

        else:
            return redirect("article_detail", pk=pk)


class ArticlePost(LoginRequiredMixin, CreateView):
    form_class = ArticlePostForm
    template_name = 'def_i/article_post.html'
    # form_valid()を使わない場合，get_initial()で初期値をユーザーにすればよい

    def get_success_url(self):
        if self.article.is_published:
            return reverse_lazy('article_published', kwargs={'pk': self.article.pk})
        else:
            return reverse_lazy('article_saved', kwargs={'pk': self.article.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info = GetIndexInfo(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            self.request.user)
        context["new_bookmarks"] = new_bookmarks
        context["new_likes"] = new_likes
        context["article_talk"] = article_talk
        context["question_talk"] = question_talk

        context["course_dict"] = pass_courses
        context["lesson_dict"] = pass_lessons
        return context

    def form_valid(self, form):
        article = form.save(commit=False)
        article.poster = self.request.user
        self.article = article
        messages.success(self.request, 'ノートを保存しました．')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'ノート保存に失敗しました．')
        super().form_invalid(form)
        self.request.session["errors"] = form.errors
        return redirect("article_failed")


class ArticlePostFailed(LoginRequiredMixin, TemplateView):
    template_name = 'def_i/post_failed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message"] = "ノート保存に失敗しました。"
        context["form"] = ArticlePostForm(self.request.POST)
        errors = self.request.session.get("errors")
        context["errors"] = errors
        del errors
        return context


class ArticlePublishedView(LoginRequiredMixin, TemplateView):
    template_name = 'def_i/article_post_suc.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message"] = "ノートを投稿しました。"
        context["form"] = ArticlePostForm()
        return context


class ArticleSavedView(LoginRequiredMixin, TemplateView):
    template_name = 'def_i/article_post_suc.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message"] = "下書きを保存しました。"
        context["form"] = ArticlePostForm()
        return context


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticlePostForm
    template_name = 'def_i/article_edit.html'

    def get_success_url(self):
        if self.article.is_published:
            return reverse_lazy('article_published', kwargs={'pk': self.article.pk})
        else:
            return reverse_lazy('article_saved', kwargs={'pk': self.article.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info = GetIndexInfo(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            self.request.user)
        context["new_bookmarks"] = new_bookmarks
        context["new_likes"] = new_likes
        context["article_talk"] = article_talk
        context["question_talk"] = question_talk

        context["course_dict"] = pass_courses
        context["lesson_dict"] = pass_lessons
        return context

    def form_valid(self, form):
        article = form.save(commit=False)
        article.poster = self.request.user
        self.article = form.save()
        messages.success(self.request, 'ノートを編集しました．')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'ノート更新に失敗しました．')
        super().form_invalid(form)
        self.request.session["errors"] = form.errors
        return redirect("article_failed")


class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    template_name = 'def_i/article_delete.html'
    success_url = reverse_lazy('article_feed')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'ノートを削除しました．')
        return super().delete(request, *args, **kwargs)


class QuestionFeed(LoginRequiredMixin, FormMixin, ListView):
    model = Question
    form_class = QuestionSearchForm
    context_object_name = "questions"
    template_name = "def_i/question_feed.html"
    paginate_by = 5
    page_kwarg = "a_page"

    def get_queryset(self):
        order_by = self.request.GET.get('orderby')
        questions = Question.objects.all().order_by('-created_at')

        if order_by == 'new':
            questions = questions.order_by('-created_at')

        elif order_by == 'unanswered':
            questions = questions.filter(
                is_answered=False).order_by('created_at')

        elif order_by == 'myquestion':
            questions = questions.filter(
                poster=self.request.user).order_by('-created_at')

        if (query_word := self.request.GET.get('keyword')):
            questions = questions.filter(
                Q(title__icontains=query_word) | Q(poster__username__icontains=query_word)
            ).order_by('-created_at')

        return questions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info = GetIndexInfo(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            self.request.user)
        context["new_bookmarks"] = new_bookmarks
        context["new_likes"] = new_likes
        context["article_talk"] = article_talk
        context["question_talk"] = question_talk

        context['orderby'] = self.request.GET.get('orderby')
        context['article'] = context["page_obj"]
        context['member'] = User.objects.annotate(
            latest_post_time=Subquery(
                Article.objects.filter(
                    poster=OuterRef('pk')).values('created_at')[:1],
            )
        ).order_by('-latest_post_time')
        return context


class QuestionDetail(LoginRequiredMixin, FormMixin, ListView):
    model = TalkAtQuestion
    form_class = QuestionTalkForm
    template_name = 'def_i/question_detail.html'

    def get(self, request, pk):
        form = QuestionTalkForm()
        question = Question.objects.get(pk=pk)
        bookmark_set = BookMark.objects.filter(
            question=question, user=request.user).values_list('question', flat=True)
        comments = question.talkatquestion_set.all().order_by('time')

        related_questions = Question.objects.filter(course=question.course).exclude(
            pk=question.pk).order_by('-created_at')[:5]
        info = GetIndexInfo(request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            request.user)

        return render(request, self.template_name, {
            "contents": question,
            "bookmark_set": bookmark_set,
            "comments": comments,
            "form": form,
            "related_questions": related_questions,

            'new_likes': new_likes,
            'new_bookmarks': new_bookmarks,
            'article_talk': article_talk,
            'question_talk': question_talk,

        })

    def post(self, request, pk):
        form = QuestionTalkForm(request.POST)
        if form.is_valid():
            messages = form.cleaned_data.get('msg')
            question = Question.objects.select_related('poster').get(pk=pk)
            question_poster = question.poster
            msg = self.model.objects.create(
                msg=messages, msg_from=request.user, msg_to=question_poster, msg_at=question)
            msg.save()
            msg.notify_new_comment()
            if not question.is_answered:  # コメントの時にブール値を編集する
                question.is_answered = True
                question.save()

            return redirect("question_detail", pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = TalkAtQuestion.objects.filter(msg_at=self.kwargs['pk'])
        context['comments_count'] = comments.count()
        context['comments'] = comments.order_by('-time')[:3]
        return context


def BookMarkView(request, pk):
    if request.method == "GET":
        question = Question.objects.get(pk=pk)
        user = request.user
        is_bookmarked = False
        bookmark = BookMark.objects.filter(question=question, user=user)

        if bookmark.exists():
            bookmark.delete()
            question.bookmark_count = F('bookmark_count')-1
            # question_poster.bookmark_count=F('bookmark_count')-1

        else:
            BookMark.objects.create(question=question, user=user)
            question.bookmark_count = F('bookmark_count')+1
            # question_poster.bookmark_count=F('bookmark_count')+1
            is_bookmarked = True

        question.save()
        # question_poster.save()
        params = {
            'question_id': question.id,
            'bookmarked': is_bookmarked,
            'bookmark_count': question.bookmark_set.count(),
        }

        return JsonResponse(params)


class QuestionPostSuc(LoginRequiredMixin, TemplateView):
    template_name = "def_i/question_post_suc.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info = GetIndexInfo(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            self.request.user)
        context["new_bookmarks"] = new_bookmarks
        context["new_likes"] = new_likes
        context["article_talk"] = article_talk
        context["question_talk"] = question_talk

        context["pk"] = self.kwargs["pk"]
        context["form"] = QuestionPostForm()
        return context


class QuestionPost(LoginRequiredMixin, CreateView):
    form_class = QuestionPostForm
    template_name = 'def_i/question_post.html'

    def get_success_url(self):
        return reverse_lazy('question_post_suc', kwargs={'pk': self.question.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course_dict"] = pass_courses
        context["lesson_dict"] = pass_lessons
        return context

    def form_valid(self, form):
        question = form.save(commit=False)
        question.poster = self.request.user
        question.save()
        self.question = question
        # push通知
        question.notify_new_question()
        messages.success(self.request, '質問を投稿しました．')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '質問作成に失敗しました．')
        super().form_invalid(form)
        self.request.session["errors"] = form.errors
        return redirect("question_failed")


class QuestionPostFailed(LoginRequiredMixin, TemplateView):
    template_name = 'def_i/post_failed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info = GetIndexInfo(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            self.request.user)
        context["new_bookmarks"] = new_bookmarks
        context["new_likes"] = new_likes
        context["article_talk"] = article_talk
        context["question_talk"] = question_talk

        context["message"] = "質問の投稿に失敗しました。"
        context["form"] = QuestionPostForm(self.request.POST)
        errors = self.request.session.get("errors")
        context["errors"] = errors
        del errors
        return context


class QuestionUpdateView(LoginRequiredMixin, UpdateView):
    model = Question
    form_class = QuestionPostForm
    template_name = 'def_i/question_edit.html'

    def get_success_url(self):
        return reverse_lazy('question_detail', kwargs={"pk": self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info = GetIndexInfo(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            self.request.user)
        context["new_bookmarks"] = new_bookmarks
        context["new_likes"] = new_likes
        context["article_talk"] = article_talk
        context["question_talk"] = question_talk

        context["course_dict"] = pass_courses
        context["lesson_dict"] = pass_lessons
        return context

    def form_valid(self, form):
        # if uploaded := self.request.POST.get('question_image_1'):
        messages.success(self.request, '質問を編集しました．')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '質問更新に失敗しました．')
        super().form_invalid(form)
        self.request.session["errors"] = form.errors
        return redirect("question_failed")


class QuestionDeleteView(LoginRequiredMixin, DeleteView):
    model = Question
    template_name = 'def_i/question_delete.html'
    success_url = reverse_lazy('question_feed')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '質問を削除しました．')
        return super().delete(request, *args, **kwargs)


class TaskQuestionPost(LoginRequiredMixin, CreateView):
    form_class = QuestionPostForm
    template_name = 'def_i/question_post.html'

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        question_at = Lesson.objects.select_related(
            "course__category").get(pk=self.kwargs['pk'])
        form_kwargs['initial'] = {
            "lesson": question_at,
            "course": question_at.course,
            "category": question_at.course.category,
        }
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info = GetIndexInfo(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            self.request.user)
        context["new_bookmarks"] = new_bookmarks
        context["new_likes"] = new_likes
        context["article_talk"] = article_talk
        context["question_talk"] = question_talk

        context["course_dict"] = pass_courses
        context["lesson_dict"] = pass_lessons
        context["pk"] = self.kwargs["pk"]
        return context

    def form_valid(self, form):
        question = form.save(commit=False)
        question.poster = self.request.user
        question.save()
        self.question = question
        question.notify_new_question()
        messages.success(self.request, '質問を投稿しました．')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '質問作成に失敗しました．')
        self.request.session["errors"] = form.errors
        super().form_invalid(form)
        return redirect("question_failed")

    def get_success_url(self):
        return reverse_lazy('question_post_suc', kwargs={"pk": self.question.pk})


class TaskArticlePost(LoginRequiredMixin, CreateView):
    form_class = ArticlePostForm
    template_name = 'def_i/article_post.html'

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        article_at = Lesson.objects.select_related(
            "course__category").get(pk=self.kwargs['pk'])
        form_kwargs['initial'] = {
            "lesson": article_at,
            "course": article_at.course,
            "category": article_at.course.category,
        }
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info = GetIndexInfo(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            self.request.user)
        context.update({
            "new_bookmarks": new_bookmarks,
            "new_likes": new_likes,
            "article_talk": article_talk,
            "question_talk": question_talk,
            "course_dict": pass_courses(),
            "lesson_dict": pass_lessons(),
            "pk": self.kwargs["pk"],
        })
        return context

    def form_valid(self, form):
        article = form.save(commit=False)
        article.poster = self.request.user
        article.save()
        self.article = article
        messages.success(self.request, 'ノートを保存しました．')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'ノート保存に失敗しました．')
        super().form_invalid(form)
        self.request.session["errors"] = form.errors
        return redirect("article_failed")

    def get_success_url(self):
        if self.article.is_published:
            return reverse_lazy('article_published', kwargs={'pk': self.article.pk})
        else:
            return reverse_lazy('article_saved', kwargs={'pk': self.article.pk})


class TaskCompleteArticlePost(TaskArticlePost):
    template_name = 'def_i/task_article_post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info = GetIndexInfo(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            self.request.user)
        context.update({
            "new_bookmarks": new_bookmarks,
            "new_likes": new_likes,
            "article_talk": article_talk,
            "question_talk": question_talk,
            "course_dict": pass_courses(),
            "lesson_dict": pass_lessons(),
            "pk": self.kwargs["pk"],
        })
        return context

    def form_valid(self, form):
        article = form.save(commit=False)
        article.poster = self.request.user
        article.for_lesson_complete = True
        article.save()
        self.article = article
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        print('フォーム保存に失敗しました。')
        super().form_invalid(form)
        self.request.session["errors"] = form.errors
        return redirect("article_failed")

    def get_success_url(self):
        if self.request.POST.get("id_clear"):
            return reverse_lazy("complete", kwargs={'pk': self.kwargs["pk"]})
        else:
            return super().get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info = GetIndexInfo(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            self.request.user)
        context.update({
            "new_bookmarks": new_bookmarks,
            "new_likes": new_likes,
            "article_talk": article_talk,
            "question_talk": question_talk,
            "course_dict": pass_courses(),
            "lesson_dict": pass_lessons(),
            "pk": self.kwargs["pk"],
            "caution": "※タブを変更しないでください！"
        })
        return context


class TaskCompleteArticleUpdate(ArticleUpdateView):
    template_name = "def_i/task_article_edit.html"

    def get_success_url(self):
        if self.request.POST.get("id_clear"):
            return reverse_lazy("complete", kwargs={'pk': self.article.lesson.pk})
        else:
            return super().get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["caution"] = "※タブを変更しないでください！"
        return context


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
        try:
            studying = StudyingCategory.objects.get(user=request.user)
        except ObjectDoesNotExist:
            studying = None

        info = GetIndexInfo(request.user)
        _, progress = info.get_progress(request.user)
        learning_lesson = info.learning_lesson
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            request.user)

        params = {
            "progress": progress,
            "studying": studying,
            "learning_lesson": learning_lesson,
            'new_likes': new_likes,
            'new_bookmarks': new_bookmarks,
            'article_talk': article_talk,
            'question_talk': question_talk,
        }
    return render(request, "def_i/course.html", params)


@require_POST
def mark_as_studying(request):
    if request.method == "POST":
        category_pk = json.loads(request.body)
        category = Category.objects.get(pk=category_pk)
        previous_cat = StudyingCategory.objects.filter(user=request.user)
        for previous in previous_cat:
            previous.delete()

        StudyingCategory.objects.create(
            user=request.user,
            category=category,
        )
        return HttpResponse("")


class CourseList(LoginRequiredMixin, ListView):
    context_object_name = 'course_and_progress'
    model = Course
    template_name = "def_i/base-task.html"

    def get_queryset(self):
        course_list = Course.objects.filter(category__title=self.kwargs['category']).order_by(
            'course_num').prefetch_related('lessons')
        progress_percent_list = []
        for course in course_list:
            lessons = course.lessons.all()
            lesson_count = lessons.count()
            cleared_lesson_count = ClearedLesson.objects.filter(
                user=self.request.user, lesson__in=lessons).count()
            if lessons:
                progress_percent = round(
                    cleared_lesson_count * 100 / lesson_count, 1)
                progress_percent_list.append(progress_percent)
        course_and_progress = [[crs, per]
                               for crs, per in zip(course_list, progress_percent_list)]
        return course_and_progress

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info = GetIndexInfo(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            self.request.user)
        context["new_bookmarks"] = new_bookmarks
        context["new_likes"] = new_likes
        context["article_talk"] = article_talk
        context["question_talk"] = question_talk

        context["category"] = self.kwargs["category"]
        return context


class TaskDetailView(LoginRequiredMixin, TemplateView):
    context_object_name = 'lesson'
    template_name = 'def_i/task_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        info = GetIndexInfo(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            self.request.user)
        context["new_bookmarks"] = new_bookmarks
        context["new_likes"] = new_likes
        context["article_talk"] = article_talk
        context["question_talk"] = question_talk
        lesson_list = Lesson.objects.filter(
            course__course_num=kwargs['course_num'], course__category__title=kwargs['category']).order_by('lesson_num')
        cleared_lesson = Lesson.objects.filter(
            cleared_lesson__user=self.request.user)
        if lesson_num := kwargs.get("lesson_num"):
            lesson = Lesson.objects.get(
                lesson_num=lesson_num, course__course_num=kwargs['course_num'], course__category__title=kwargs['category'])
        else:
            lesson = Lesson.objects.get(
                lesson_num=1, course__course_num=kwargs['course_num'], course__category__title=kwargs['category'])
        context["lesson"] = lesson
        context['lesson_list'] = lesson_list
        context['cleared_lesson'] = cleared_lesson
        context["category"] = Category.objects.filter(
            title=kwargs['category']).first()
        context["article_for_complete"] = Article.objects.filter(
            poster=self.request.user,
            lesson=lesson,
            for_lesson_complete=True,
        ).first()
        context["is_cleared"] = ClearedLesson.objects.filter(
            user=self.request.user,
            lesson=lesson,
        )
        context["next_lesson"] = info.learning_lesson
        return context


@login_required(login_url='accounts/login/')
def lesson_complete(request, pk):
    if request.method == "GET":
        user = request.user
        lesson = Lesson.objects.get(pk=pk)
        ClearedLesson.objects.get_or_create(user=user, lesson=lesson)
        # if next_lesson := Lesson.objects.filter(pk=pk+1).first():
        # もしまだ学習中にするボタンを押していなかったらここでStudyingCategoryを作る
        if studying := StudyingCategory.objects.filter(user=user):
            for s in studying:
                s.delete()
        StudyingCategory.objects.get_or_create(
            user=user,
            category=lesson.course.category,
        )
        return redirect('task_detail', lesson.course.category, lesson.course.course_num, lesson.lesson_num)


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
            questions = questions.filter(is_answered=False)

        return questions

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        info = GetIndexInfo(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            self.request.user)
        context["new_bookmarks"] = new_bookmarks
        context["new_likes"] = new_likes
        context["article_talk"] = article_talk
        context["question_talk"] = question_talk
        context['orderby'] = self.request.GET.get('orderby')
        user = self.request.user
        lesson = Lesson.objects.get(pk=self.kwargs['pk'])
        my_question_list = Question.objects.filter(
            poster=user).order_by('-created_at')
        context['lesson'] = lesson
        context['my_question_list'] = my_question_list

        return context


class TaskArticle(LoginRequiredMixin, ListView):
    model = Article
    template_name = "def_i/task_article.html"
    paginate_by = 5

    def get_queryset(self):
        order_by = self.request.GET.get('orderby')
        lesson = Lesson.objects.get(pk=self.kwargs['pk'])
        articles = Article.objects.filter(
            lesson=lesson).filter(is_published=True)
        if order_by == 'new':
            articles = articles.order_by('-created_at')

        elif order_by == 'like':
            articles = articles.order_by('-like_count', '-created_at')

        if (query_word := self.request.GET.get('keyword')):  # 代入式
            articles = articles.filter(
                Q(title__icontains=query_word) | Q(
                    poster__username__icontains=query_word)
            )

        return articles

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        info = GetIndexInfo(self.request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            self.request.user)
        context["new_bookmarks"] = new_bookmarks
        context["new_likes"] = new_likes
        context["article_talk"] = article_talk
        context["question_talk"] = question_talk
        context['orderby'] = self.request.GET.get('orderby')
        user = self.request.user
        pk = self.kwargs['pk']
        lesson = Lesson.objects.get(pk=pk)
        my_article_list = Article.objects.filter(
            lesson=lesson, poster=user).order_by('-created_at')
        context['lesson'] = lesson
        context['my_article_list'] = my_article_list

        return context


@login_required(login_url='accounts/login/')
def note_list(request):
    return render(request, "def_i/note_list.html")


class MessageNotification(LoginRequiredMixin, TemplateView):
    template_name = 'def_i/message_notification.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    # 記事と質問のTalkを回収して，Unionさせている．Unionによって消えてしまう情報(Title,pk)をannotateしている
        msg_article = TalkAtArticle.objects.annotate(
            msg_at_title=Subquery(
                Article.objects.filter(pk=OuterRef(
                    'msg_at')).values('title')[:1]
            ),
            msg_at_pk=Subquery(
                Article.objects.filter(pk=OuterRef('msg_at')).values('pk')[:1]
            )
        ).filter(msg_to=self.request.user.id)

        msg_question = TalkAtQuestion.objects.annotate(
            msg_at_title=Subquery(
                Question.objects.filter(
                    pk=OuterRef('msg_at')).values('title')[:1]
            ),
            msg_at_pk=Subquery(
                Question.objects.filter(pk=OuterRef('msg_at')).values('pk')[:1]
            )
        ).filter(msg_to=self.request.user.id)
        msg_union = msg_article.union(msg_question).order_by('-time')
        context["messages"] = msg_union
        return context


def LikeView(request, pk):
    if request.method == "GET":
        article = Article.objects.get(pk=pk)  # filterでないとF&updateが使えにゃい
        article_poster = article.poster
        user = request.user
        is_liked = False
        like = Like.objects.filter(article=article, user=user)

        if like.exists():
            like.delete()
            article.like_count = F('like_count')-1
            article_poster.like_count = F('like_count')-1

        else:
            like.create(article=article, user=user)
            article.like_count = F('like_count')+1
            article_poster.like_count = F('like_count')+1
            is_liked = True

        article.save()
        article_poster.save()
        params = {
            'article_id': article.id,
            'liked': is_liked,
            'count': article.like_set.count(),
        }

        return JsonResponse(params)


@login_required(login_url='accounts/login/')
def mypage_view(request):
    user = request.user
    orderby = request.GET.get('orderby')
    question = Question.objects.order_by('created_at')
    if orderby == 'like':
        question_like = question.filter(bookmark__user=user)
        paginator = Paginator(question_like, 5)
    else:
        question = question.filter(poster=user)
        paginator = Paginator(question, 5)

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
        paginator = Paginator(article_like, 5)
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

    try:
        studying = StudyingCategory.objects.get(user=user)
    except ObjectDoesNotExist:
        studying = None

    info = GetIndexInfo(request.user)
    _, progress = info.get_progress(request.user)
    learning_lesson = info.learning_lesson
    new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
        request.user)

    params = {
        'each_progress': progress,
        'question': question,
        'article': article,
        'studying': studying,
        'learning_lesson': learning_lesson,

        'new_likes': new_likes,
        'new_bookmarks': new_bookmarks,
        'article_talk': article_talk,
        'question_talk': question_talk,
    }
    return render(request, 'def_i/my_page.html', params)


@login_required(login_url='accounts/login/')
def userpage_view(request, pk):
    user = User.objects.get(pk=pk)
    question = Question.objects.order_by('created_at').filter(poster=user)

    paginator = Paginator(question, 5)
    page = request.GET.get('q_page')

    try:
        question = paginator.page(page)
    except PageNotAnInteger:
        question = paginator.page(1)
    except EmptyPage:
        question = paginator.page(paginator.num_pages)

    article = Article.objects.order_by('-created_at').filter(poster=user)

    paginator = Paginator(article, 5)
    page = request.GET.get('page')

    try:
        article = paginator.page(page)
    except PageNotAnInteger:
        article = paginator.page(1)
    except EmptyPage:
        article = paginator.page(paginator.num_pages)

    try:
        studying = StudyingCategory.objects.get(user=user)
    except ObjectDoesNotExist:
        studying = None
    info = GetIndexInfo(user)
    _, progress = info.get_progress(user)
    learning_lesson = info.learning_lesson
    new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
        request.user)

    params = {
        'each_progress': progress,
        'learning_lesson': learning_lesson,
        'question': question,
        'article': article,
        'user_data': user,
        'studying': studying,

        'new_likes': new_likes,
        'new_bookmarks': new_bookmarks,
        'article_talk': article_talk,
        'question_talk': question_talk,

    }
    return render(request, 'def_i/user_page.html', params)


@csrf_exempt
def callback(request):
    return handle_callback(request)


def notify(request):
    if request.method == "GET":

        info = GetIndexInfo(request.user)
        new_likes, new_bookmarks, article_talk, question_talk = info.get_notification(
            request.user)
        for like in new_likes:
            like.has_noticed = True
            like.save()
        for bookmark in new_bookmarks:
            bookmark.has_noticed = True
            bookmark.save()
        for talk in article_talk:
            talk.has_noticed = True
            talk.save()
        for talk in question_talk:
            talk.has_noticed = True
            talk.save()
        params = {
            "is_notified": True,
        }
        return JsonResponse(params)
