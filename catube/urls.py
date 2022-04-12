from django.urls import path, re_path

# from . import views_cbv as views
from . import views_fbv as views

app_name = "catube"

urlpatterns = [
    path("", views.video_list, name="video_list"),
    path("new/", views.video_new, name="video_new"),
    path("<int:pk>/", views.video_detail, name="video_detail"),
    path("<int:pk>/edit/", views.video_edit, name="video_edit"),
    path("<int:pk>/delete", views.video_delete, name="video_delete"),
    re_path(
        r"^(?P<pk>\d+)/(?P<action>(like|dislike))/$",
        views.video_like,
        name="video_like",
    ),
    path(
        "<int:video_pk>/comments/new/",
        views.comment_new,
        name="comment_new",
    ),
    path(
        "<int:video_pk>/comments/<int:pk>/delete/",
        views.comment_delete,
        name="comment_delete",
    ),
]
