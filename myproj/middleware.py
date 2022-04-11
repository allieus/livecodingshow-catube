import zoneinfo

from django.utils import timezone


# refs: https://docs.djangoproject.com/ko/4.0/topics/i18n/timezones/#selecting-the-current-time-zone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.session.get("django_timezone", "Asia/Seoul")
        if tzname:
            timezone.activate(zoneinfo.ZoneInfo(tzname))
        else:
            timezone.deactivate()
        return self.get_response(request)
