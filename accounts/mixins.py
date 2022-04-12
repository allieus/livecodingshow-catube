from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin as DjangoLoginRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin as DjangoUserPassesTestMixin


class HandleNoPermissionMixin:
    def handle_no_permission(self):
        response = super().handle_no_permission()
        messages.warning(self.request, "페이지 접근을 위해 인증이 필요합니다.")
        return response


class LoginRequiredMixin(HandleNoPermissionMixin, DjangoLoginRequiredMixin):
    pass


class UserPassesTestMixin(HandleNoPermissionMixin, DjangoUserPassesTestMixin):
    pass
