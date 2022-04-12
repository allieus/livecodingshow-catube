from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator, InvalidPage
from django.db.models import OuterRef, Exists, F
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404

from catube.forms import VideoForm, CommentForm
from catube.models import Video, Comment


User = get_user_model()


def video_list(request: HttpRequest) -> HttpResponse:
    qs = Video.objects.all()
    paginate_by = 12
    bootstrap_pagination_extra_list = []

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(title__icontains=q)
        bootstrap_pagination_extra_list.append(f"q={q}")

    is_filter_liked = "liked" in request.GET
    if is_filter_liked:
        qs = qs.filter(liked_user_set=request.user)
        bootstrap_pagination_extra_list.append("liked=1")

    if request.user.is_authenticated:
        subquery = User.objects.filter(
            username=request.user.username,
            liked_video_set=OuterRef("pk"),
        )
        qs = qs.annotate(is_liked=Exists(subquery))

    paginator = Paginator(qs, paginate_by)

    page_number = int(request.GET.get("page", 1))
    try:
        page = paginator.page(page_number)
    except InvalidPage:
        raise Http404

    return render(
        request,
        "catube/video_list.html",
        {
            "paginator": paginator,
            "page_obj": page,
            "video_list": page.object_list,
            "is_paginated": page.has_other_pages(),
            "bootstrap_pagination_extra": "&".join(bootstrap_pagination_extra_list),
            "q": q,
            "is_filter_liked": is_filter_liked,
        },
    )


@login_required
def video_new(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.author = request.user
            video.save()
            messages.success(request, "새로운 비디오를 저장했습니다. :D")
            return redirect(video)
    else:
        form = VideoForm()

    return render(
        request,
        "form.html",
        {
            "form": form,
            "form_title": "새 비디오 등록",
        },
    )


def video_detail(request: HttpRequest, pk: int) -> HttpResponse:
    Video.objects.filter(pk=pk).update(view_count=F("view_count") + 1)
    video = get_object_or_404(Video, pk=pk)
    return render(
        request,
        "catube/video_detail.html",
        {
            "video": video,
            "comment_form": CommentForm(),
        },
    )


def video_edit(request: HttpRequest, pk: int) -> HttpResponse:
    video = get_object_or_404(Video, pk=pk)
    if request.user != video.author:
        messages.warning(request, "페이지 접근을 위해 인증이 필요합니다.")
        return redirect_to_login(request.path)

    if request.method == "POST":
        form = VideoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            video = form.save(commit=False)
            video.author = request.user
            video.save()
            messages.success(request, "비디오 변경내역을 저장했습니다. :D")
            return redirect(video)
    else:
        form = VideoForm(instance=video)

    return render(
        request,
        "form.html",
        {
            "form": form,
            "form_title": "비디오 수정",
        },
    )


def video_delete(request: HttpRequest, pk: int) -> HttpResponse:
    video = get_object_or_404(Video, pk=pk)
    if request.user != video.author:
        messages.warning(request, "페이지 접근을 위해 인증이 필요합니다.")
        return redirect_to_login(request.path)

    if request.method == "POST":
        video.delete()
        messages.success(request, "지정 비디오를 삭제했습니다.")
        return redirect("catube:video_list")

    return render(
        request,
        "catube/video_confirm_delete.html",
        {
            "video": video,
        },
    )


@login_required
def video_like(request: HttpRequest, pk: int, action: str) -> HttpResponse:
    video = get_object_or_404(Video, pk=pk)
    if action == "like":
        video.liked_user_set.add(request.user)
    else:
        video.liked_user_set.remove(request.user)
    return redirect(video)


@login_required
def comment_new(request: HttpRequest, video_pk: int) -> HttpResponse:
    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.video = get_object_or_404(Video, pk=video_pk)
            comment.save()
            messages.success(request, "새 댓글을 저장했습니다. ;-)")
            return redirect("catube:video_detail", video_pk)
    else:
        form = CommentForm()

    return render(
        request,
        "form.html",
        {
            "form": form,
            "form_title": "새로운 댓글 등록",
        },
    )


def comment_delete(request: HttpRequest, video_pk: int, pk: int) -> HttpResponse:
    comment = get_object_or_404(Comment, pk=pk)
    if request.user != comment.author:
        messages.warning(request, "페이지 접근을 위해 인증이 필요합니다.")
        return redirect_to_login(request.path)

    if request.method == "POST":
        comment.delete()
        messages.success(request, "지정 댓글을 삭제했습니다.")
        return redirect("catube:video_detail", video_pk)

    return render(
        request,
        "catube/comment_confirm_delete.html",
        {
            "comment": comment,
        },
    )
