from django.conf import settings
from django.db import models
from django.urls import reverse


class Video(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField()
    photo = models.ImageField()
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tag_set = models.ManyToManyField("Tag", blank=True)
    liked_user_set = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="liked_video_set"
    )

    def get_absolute_url(self):
        return reverse("catube:video_detail", args=[self.pk])

    class Meta:
        ordering = ["-id"]


class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]


# 직접 구현보다 django-taggit 라이브러리 좋습니다.


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
