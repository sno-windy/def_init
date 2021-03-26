from django import forms
from django.contrib.auth.admin import UserCreationForm
from allauth.account.forms import SignupForm, LoginForm
from .models import User

class MyCustomSignupForm(SignupForm):
    position = forms.CharField()
    user_image = forms.ImageField(required=False)
    class Meta:
        model = User
        fields = ['username', 'email', 'position', 'user_image', 'password']

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