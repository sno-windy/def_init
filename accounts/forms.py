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
        fields = ['username', 'email', 'password1', 'password2', 'position', 'user_image']


    def save(self, request):
    
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(MyCustomSignupForm, self).save(request)

        # Add your own processing here.
        user.position = request.POST.get('position')
        user.user_image = request.FILES.get('user_image')
        user.save()

        # You must return the original result.
        return user

class MyCustomLoginForm(LoginForm):
    
    def login(self, *args, **kwargs):

        # Add your own processing here.

        # You must return the original result.
        return super(MyCustomLoginForm, self).login(*args, **kwargs)

class UserChangeForm(MyCustomSignupForm):
    user_image = forms.ImageField(required=False)
    
    def __init__(self, email=None, username=None, position=None, password1=None, password2=None, user_image=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)
        # ユーザーの更新前情報をフォームに挿入
        if email:
            self.fields['email'].widget.attrs['value'] = email
        if username:
            self.fields['username'].widget.attrs['value'] = username
        if position:
            self.fields['position'].widget.attrs['value'] = position
        if password1:
            self.fields['password1'].widget.attrs['value'] = password1
        if password2:
            self.fields['password2'].widget.attrs['value'] = password2
        if user_image:
            self.fields['user_image'].widget.attrs['value'] = user_image

    def update(self, user):
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        user.position = self.cleaned_data['position']
        user.user_image = self.cleaned_data['user_image']
        user.password1 = self.cleaned_data['password1']
        user.password2 = self.cleaned_data['password2']
        user.save()
