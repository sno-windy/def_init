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
        fields = ['title','content','poster',]
        widgets = {
            'poster':forms.HiddenInput
        }

class QuestionTalkForm(forms.ModelForm):
    class Meta:
        model = TalkAtQuestion
        fields = ['msg',]

class QuestionPostForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title','content','poster',]
        widgets = {
            'poster':forms.HiddenInput
        }


