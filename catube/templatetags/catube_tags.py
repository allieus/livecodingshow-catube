from django import template


register = template.Library()


@register.simple_tag
def is_liked_user(video, user):
    return video.liked_user_set.filter(username=user.username).exists()
