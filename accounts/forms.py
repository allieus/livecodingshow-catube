from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'last_name', 'first_name']

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            qs = User.objects.filter(email=email)
            qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("이미 등록된 이메일 주소입니다.")

        return email
