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

class MemoForm(forms.ModelForm):
    class Meta:
        model = Memo
        fields = ['contents',]
