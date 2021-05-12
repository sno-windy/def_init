from django import forms
from markdownx.widgets import MarkdownxWidget
from .models import (
    User, Article, Question, Like, Lesson, Talk, TalkAtArticle, TalkAtQuestion, Course, Category
)
from django.contrib.auth.forms import (
    AuthenticationForm
)


class ArticleTalkForm(forms.ModelForm):
    class Meta:
        model = TalkAtArticle
        fields = ['msg',]
        widgets = {
            'msg': MarkdownxWidget(
                attrs={'placeholder': 'あなたの回答を入力（コードを含む場合はMarkdown記法をご使用ください）'}
            )
        }

class ArticlePostForm(forms.ModelForm):
    category = forms.ModelChoiceField(Category.objects.all(), empty_label='カテゴリーをタブから選択')
    course = forms.ModelChoiceField(Course.objects.all(), empty_label='コースをタブから選択')
    lesson = forms.ModelChoiceField(Lesson.objects.all(), empty_label='レッスンをタブから選択')

    class Meta:
        model = Article
        fields = ['is_published', 'title', 'category', 'course', 'lesson', 'content','article_image_1','article_image_2']
        labels = {
            'title':'',
            'content':'',
        }
        widgets = {
            'title': forms.TextInput(
                attrs={'placeholder':'記事タイトル：30文字以内'}
            ),
            'content': MarkdownxWidget(
                attrs={'placeholder':'本文を入力（コードを含む場合はMarkdown記法をご使用ください）<br> * 実現したいこと <br> * 試したこと <br> * 出力されたエラー <br> などを書きましょう'}
            )
        }

class QuestionTalkForm(forms.ModelForm):
    class Meta:
        model = TalkAtQuestion
        fields = ['msg',]
        widgets = {
            'msg': MarkdownxWidget(
                attrs={'placeholder': 'あなたの回答を入力（コードを含む場合はMarkdown記法をご使用ください）'}
            )
        }

class QuestionPostForm(forms.ModelForm):
    category = forms.ModelChoiceField(Category.objects.all(), empty_label='カテゴリーをタブから選択')
    course = forms.ModelChoiceField(Course.objects.all(), empty_label='コースをタブから選択')
    lesson = forms.ModelChoiceField(Lesson.objects.all(), empty_label='レッスンをタブから選択')

    class Meta:
        model = Question
        fields = ['title', 'category', 'lesson', 'course', 'content', 'question_image_1', 'question_image_2']
        labels = {
            'title':'',
            'category': '',
            'lesson': '',
            'course': '',
            'content':'',
        }
        # emply_label = '選択してください'
        widgets = {
            'title': forms.TextInput(
                attrs={'placeholder':'質問タイトル：30文字以内'}
            ),
            'content': MarkdownxWidget(
                attrs={'placeholder':'本文を入力（コードを含む場合はMarkdown記法をご使用ください）&#13;・実現したいこと&#13;・試したこと&#13;・出力されたエラー&#13;などを書きましょう'}
            )
        }



class ArticleSearchForm(forms.Form):
    keyword = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'ノートを検索'}
        )
    )


class QuestionSearchForm(forms.Form):
    keyword = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': '質問を検索'}
        )
    )
