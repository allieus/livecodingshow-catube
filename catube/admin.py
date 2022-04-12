from django.contrib import admin
from .models import Video, Comment


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ["pk", "title", "view_count", "author", "created_at"]
    list_display_links = ["title"]
    search_fields = ["title", "author__username"]
    list_filter = ["created_at"]


admin.site.register(Comment)
