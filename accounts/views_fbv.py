from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache

from accounts.forms import SignupForm, ProfileForm


@never_cache
def signup(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "환영합니다. :-)")
            return redirect(settings.LOGIN_URL)
    else:
        form = SignupForm()

    return render(
        request,
        "form.html",
        {
            "form": form,
        },
    )


@never_cache
def login(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST, files=request.FILES)
        if form.is_valid():
            before = form.get_user().last_login
            auth_login(request, form.get_user())
            if before is None:
                welcome_message = "첫 로그인이시네요. 반갑습니다. :-)"
            else:
                diff_minutes = int((timezone.now() - before).total_seconds() // 60)
                if diff_minutes == 0:
                    welcome_message = "방금 전에도 로그인하셨었는데 ;-)"
                else:
                    welcome_message = f"{diff_minutes}분 만이네요. :-)"

            messages.success(request, f"{form.get_user().username}님. {welcome_message}")
            next_url = request.GET.get("next", settings.LOGIN_REDIRECT_URL)
            return redirect(next_url)
    else:
        form = AuthenticationForm(request)

    return render(
        request,
        "form.html",
        {
            "form": form,
        },
    )


@never_cache
def logout(request: HttpRequest) -> HttpResponse:
    auth_logout(request)
    messages.success(request, f"곧 또 만나요. ;-)")
    next_url = request.GET.get("next", settings.LOGOUT_REDIRECT_URL)
    return redirect(next_url or settings.LOGIN_URL)


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    return render(request, "accounts/profile.html")


@login_required
def profile_edit(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "프로필을 저장했습니다.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(
        request,
        "form.html",
        {
            "form": form,
            "form_title": "프로필 수정",
        },
    )
