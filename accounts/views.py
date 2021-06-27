from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView
from django.views.generic.edit import UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.views import ( PasswordChangeView,  PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView)
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from allauth.account.views import SignupView, login, logout, signup, PasswordChangeView
from allauth.socialaccount.views import SignupView as SocialSignupView
from .models import User
from .forms import MyCustomSignupForm, UserChangeForm, UserPasswordResetForm, MyCustomSocialSignupForm


class MySignupView(SignupView):
    form_class = MyCustomSignupForm


@method_decorator(login_required, name='dispatch')
class UserChangeView(UpdateView):
    model = User
    form_class = UserChangeForm
    template_name = "account/change.html"
    success_url = "/"

    def get_object(self):
        return self.request.user

change = UserChangeView.as_view()

class PasswordChange(PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = PasswordChangeForm
    success_url = '/'
    template_name = 'account/password_change.html'


class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    email_template_name = 'account/mail_template/password_reset/message.txt'
    form_class = UserPasswordResetForm
    subject_template_name = 'account/mail_template/password_reset/subject.txt'
    success_url = reverse_lazy('password_reset_done')
    template_name = 'account/password_reset_form.html'


class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ"""
    template_name = 'account/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    form_class = SetPasswordForm
    success_url = reverse_lazy('account_login')
    template_name = 'account/password_reset_confirm.html'


class CustomSocialSignupView(SocialSignupView):
    form_class = MyCustomSocialSignupForm
    template_name = 'socialaccount/signup.html'
