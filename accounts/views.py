from django.shortcuts import render,reverse,redirect
from .forms import  MyCustomSignupForm, MyCustomLoginForm
from allauth.account.views import LoginView, SignupView, LogoutView, login, logout, signup


class MySignupView(SignupView):
    form_class = MyCustomSignupForm
