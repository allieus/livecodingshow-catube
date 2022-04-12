from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.validators import phone_number_validator


class User(AbstractUser):
    pass


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(
        max_length=11,
        blank=True,
        validators=[phone_number_validator],
        verbose_name="휴대폰 번호",
    )
