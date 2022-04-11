from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from accounts.forms import ProfileForm

signup = CreateView.as_view(
    form_class=UserCreationForm,
    template_name='form.html',
    success_url=settings.LOGIN_URL,
)


login = LoginView.as_view(
    template_name='form.html',
)


logout = LogoutView.as_view(
    next_page=settings.LOGIN_URL,
)


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


profile_edit = ProfileUpdateView.as_view()
