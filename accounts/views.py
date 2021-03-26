from django.shortcuts import render,reverse,redirect
from django.views.generic import FormView
from .forms import  MyCustomSignupForm, MyCustomLoginForm
from allauth.account.views import LoginView, SignupView, LogoutView, login, logout, signup


class MySignupView(SignupView):
    form_class = MyCustomSignupForm
    

class UserChangeView(LoginRequiredMixin, FormView):
    template_name = 'account/change.html'
    form_class = UserChangeForm
    success_url = reverse_lazy('account_mypage')

    def form_valid(self, form):
        #formのupdateメソッドにログインユーザーを渡して更新
        form.update(user=self.request.user)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 更新前のユーザー情報をkwargsとして渡す
        kwargs.update({
            'email' : self.request.user.email,
            'username' : self.request.user.username,
            'position' : self.request.user.position,
            'password1' : self.request.user.password1,
            'password2' : self.request.user.password2,
            'user_image' : self.request.user.user_image,
        })
        return kwargs


change = UserChangeView.as_view()
