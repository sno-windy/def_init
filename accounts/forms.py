from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import PasswordChangeForm,PasswordResetForm, SetPasswordForm
from allauth.account.forms import SignupForm, LoginForm
from .models import User

class MyCustomSignupForm(SignupForm):
    position = forms.CharField()
    user_image = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # django-allauthのフィールドを上書き
        self.fields['position'].widget.attrs['placeholder'] = '15文字以下'
        self.fields['email'].widget.attrs['placeholder'] = 'メールアドレス'
        self.fields['password1'].widget.attrs['placeholder'] = '8文字以上の十分に複雑なもの'
        self.fields['password2'].widget.attrs['placeholder'] = '8文字以上の十分に複雑なもの'

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

class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email',  'position', 'user_image']

    def update(self):
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        user.position = self.cleaned_data['position']
        user.user_image = self.cleaned_data['user_image']
        user.save()
