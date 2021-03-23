from django import forms
from .models import User, Article, Question, Like, Task, Talk, TalkAtArticle, TalkAtQuestion
from allauth.account.forms import LoginForm, SignupForm
from django.contrib.auth.forms import (
    AuthenticationForm
)
# class LoginForm(AuthenticationForm):
#     """ログインフォーム"""

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field in self.fields.values():
#             field.widget.attrs['class'] = 'form-control'
#             field.widget.attrs['placeholder'] = field.label

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
class MyCustomLoginForm(LoginForm):
    def login(self, *args, **kwargs):

        # Add your own processing here.

        # You must return the original result.
        return super(MyCustomLoginForm, self).login(*args, **kwargs)

class MyCustomSignupForm(SignupForm):

    def save(self, request):

        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(MyCustomSignupForm, self).save(request)

        # Add your own processing here.

        # You must return the original result.
        return user
