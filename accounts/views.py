from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, UpdateView

from accounts.forms import ProfileForm


class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'form.html'
    success_url = settings.LOGIN_URL

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "환영합니다. :-)")
        return response


signup = SignupView.as_view()


class MyLoginView(LoginView):
    template_name = "form.html"

    def form_valid(self, form):
        before = form.get_user().last_login
        response = super().form_valid(form)
        diff_minutes = int((timezone.now() - before).total_seconds() // 60)
        if diff_minutes == 0:
            welcome_message = "방금 전에도 로그인하셨었는데 ;-)"
        else:
            welcome_message = f"{diff_minutes}분 만이네요. :-)"

        messages.success(self.request, f"{form.get_user().username}님. {welcome_message}")

        return response


login = MyLoginView.as_view()


class MyLogoutView(LogoutView):
    next_page = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(self.request, f"곧 또 만나요. ;-)")
        return response


logout = MyLogoutView.as_view()


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = "form.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["form_title"] = "프로필 수정"
        return context_data

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "프로필을 저장했습니다.")
        return response


profile_edit = ProfileUpdateView.as_view()
