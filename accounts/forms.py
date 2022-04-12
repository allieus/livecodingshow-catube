from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from accounts.models import Profile
from accounts.validators import phone_number_validator


User = get_user_model()


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User


class ProfileForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=13,
        validators=[phone_number_validator],
        label=Profile._meta.get_field("phone_number").verbose_name,
    )

    class Meta:
        model = User
        fields = ["email", "last_name", "first_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            try:
                self.fields["phone_number"].initial = self.instance.profile.phone_number
            except Profile.DoesNotExist:
                pass

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            qs = User.objects.filter(email=email)
            qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("이미 등록된 이메일 주소입니다.")

        return email

    def save(self, commit=True):
        saved_instance = super().save(commit)

        profile, __ = Profile.objects.get_or_create(user=saved_instance)

        phone_number = self.cleaned_data.get("phone_number", "")
        profile.phone_number = phone_number
        profile.save()

        return saved_instance
