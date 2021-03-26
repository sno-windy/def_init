from django import forms
from django.forms import ModelForm
from django.contrib.auth.admin import UserCreationForm
from allauth.account.forms import SignupForm, LoginForm
from .models import User

class MyCustomSignupForm(SignupForm):
    position = forms.CharField()
    user_image = forms.ImageField(required=False)
    class Meta:
        model = User
        fields = [ 'position', 'user_image']

    def save(self, request):
    
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(MyCustomSignupForm, self).save(request)

        # Add your own processing here.
        user.user_image = request.FILES.get('user_image')
        user.save()

        # You must return the original result.
        return user

class MyCustomLoginForm(LoginForm):
    
    def login(self, *args, **kwargs):

        # Add your own processing here.

        # You must return the original result.
        return super(MyCustomLoginForm, self).login(*args, **kwargs)

class UserChangeForm(ModelForm):
    class Meta:
        model = User
        fields = [ 'position', 'user_image']

    # def __init__(self, email=None, first_name=None, last_name=None, *args, **kwargs):
    #     kwargs.setdefault('label_suffix', '')
    #     super().__init__(*args, **kwargs)
    #     # ユーザーの更新前情報をフォームに挿入
    #     if email:
    #         self.fields['email'].widget.attrs['value'] = email
    #     if first_name:
    #         self.fields['first_name'].widget.attrs['value'] = first_name
    #     if last_name:
    #         self.fields['last_name'].widget.attrs['value'] = last_name
    def update(self, user):
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        user.position = self.cleaned_data['position']
        user.user_image = self.cleaned_data['user_image']
        user.password1 = self.cleaned_data['password1']
        user.password2 = self.cleaned_data['password2']
        user.save()
