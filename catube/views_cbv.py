from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import F, Exists, OuterRef
from django.shortcuts import get_object_or_404, resolve_url, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DeleteView,
    UpdateView,
    DetailView,
    CreateView,
)

from accounts.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Video, Comment
from .forms import VideoForm, CommentForm


User = get_user_model()


class VideoListView(ListView):
    model = Video
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(title__icontains=q)

        if "liked" in self.request.GET:
            qs = qs.filter(liked_user_set=self.request.user)

        if self.request.user.is_authenticated:
            subquery = User.objects.filter(
                username=self.request.user.username, liked_video_set=OuterRef("pk")
            )
            qs = qs.annotate(is_liked=Exists(subquery))

        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context_data = super().get_context_data(object_list=object_list, **kwargs)
        if "liked" in self.request.GET:
            context_data["bootstrap_pagination_extra"] = "liked=1"
        return context_data


video_list = VideoListView.as_view()


class VideoCreateView(LoginRequiredMixin, CreateView):
    model = Video
    form_class = VideoForm
    template_name = "form.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["form_title"] = "새 비디오 등록"
        return context_data

    def form_valid(self, form):
        video = form.save(commit=False)
        video.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "새로운 비디오를 저장했습니다. :D")
        return response


video_new = VideoCreateView.as_view()


class VideoDetailView(DetailView):
    model = Video

    def get(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        Video.objects.filter(pk=pk).update(view_count=F("view_count") + 1)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["comment_form"] = CommentForm()
        return context_data


video_detail = VideoDetailView.as_view()


class VideoUpdateView(UserPassesTestMixin, UpdateView):
    model = Video
    form_class = VideoForm
    template_name = "form.html"

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["form_title"] = "비디오 수정"
        return context_data

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "비디오 변경내역을 저장했습니다. :D")
        return response


video_edit = VideoUpdateView.as_view()


class VideoDeleteView(UserPassesTestMixin, DeleteView):
    model = Video
    success_url = reverse_lazy("catube:video_list")

    def test_func(self):
        return self.request.user == self.get_object().author

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "지정 비디오를 삭제했습니다.")
        return response


video_delete = VideoDeleteView.as_view()


class VideoLikeView(LoginRequiredMixin, DetailView):
    model = Video

    def get(self, request, *args, **kwargs):
        video = self.get_object()
        if self.kwargs["action"] == "like":
            video.liked_user_set.add(request.user)
        else:
            video.liked_user_set.remove(request.user)
        return redirect(video)


video_like = VideoLikeView.as_view()


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "form.html"

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.video = get_object_or_404(Video, pk=self.kwargs["video_pk"])
        response = super().form_valid(form)
        messages.success(self.request, "새 댓글을 저장했습니다. ;-)")
        return response

    def get_success_url(self):
        return resolve_url("catube:video_detail", self.kwargs["video_pk"])


comment_new = CommentCreateView.as_view()


class CommentDeleteView(UserPassesTestMixin, DeleteView):
    model = Comment

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_success_url(self):
        return resolve_url("catube:video_detail", self.kwargs["video_pk"])

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "지정 댓글을 삭제했습니다.")
        return response


comment_delete = CommentDeleteView.as_view()
