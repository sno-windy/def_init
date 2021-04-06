from django import forms
from .models import User, Article, Question, Like, Task, Talk, TalkAtArticle, TalkAtQuestion
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
        # widgets = {
        #     'poster':forms.HiddenInput
        # } #フォームバリッド関数を使わない場合

class QuestionTalkForm(forms.ModelForm):
    class Meta:
        model = TalkAtQuestion
        fields = ['msg',]

class QuestionPostForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title','content',]

class ArticleSearchForm(forms.Form):
    keyword = forms.CharField(label='', required=False, widget=forms.TextInput(attrs={'placeholder': 'タイトルorユーザー名'}))
