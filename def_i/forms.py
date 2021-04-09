from django import forms
from .models import User, Article, Question, Like, Task, Talk, TalkAtArticle, TalkAtQuestion, Task, Task_Sub, Memo
from django.contrib.auth.forms import (
    AuthenticationForm
)


class ArticleTalkForm(forms.ModelForm):
    class Meta:
        model = TalkAtArticle
        fields = ['msg',]

class ArticlePostForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title','content',]
        labels = {
            'title':'',
            'content':'',
        }
        widgets = {
            'title': forms.TextInput(
                attrs={'placeholder':'記事タイトル：30文字以内'}
            ),
            'content': forms.Textarea(
                attrs={'placeholder':'マークダウンで書くことができます！'}
            )
        }

class QuestionTalkForm(forms.ModelForm):
    class Meta:
        model = TalkAtQuestion
        fields = ['msg',]

class QuestionPostForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title','content',]
        labels = {
            'title':'',
            'content':'',
        }
        widgets = {
            'title': forms.TextInput(
                attrs={'placeholder':'質問タイトル：30文字以内'}
            ),
            'content': forms.Textarea(
                attrs={'placeholder':'マークダウンで書くことができます！'}
            )
        }


class MemoForm(forms.ModelForm):
    class Meta:
        model = Memo
        fields = ['contents',]

class ArticleSearchForm(forms.Form):
    keyword = forms.CharField(label='', required=False, widget=forms.TextInput(attrs={'placeholder': 'タイトルorユーザー名'}))
