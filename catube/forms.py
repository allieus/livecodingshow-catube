import os
import re

from django import forms
from .models import Video, Comment, Tag


class VideoForm(forms.ModelForm):
    tag_names = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            tag_names = [tag.name for tag in self.instance.tag_set.all()]
            self.fields["tag_names"].initial = ", ".join(tag_names)

    def clean_file(self):
        file = self.cleaned_data.get("file", None)
        if file:
            extension = os.path.splitext(file.name)[-1].lower()
            if extension not in (".mp4", ".avi"):
                raise forms.ValidationError("비디오 파일을 업로드해주세요.")
        return file

    def _save_m2m(self):
        super()._save_m2m()

        tag_names = self.cleaned_data.get("tag_names", "")
        if tag_names:
            tag_list = []
            for tag_name in tag_names.split(","):
                tag_name = re.sub(r"\s+", " ", tag_name).strip()
                tag, __ = Tag.objects.get_or_create(name=tag_name)
                tag_list.append(tag)
            self.instance.tag_set.set(tag_list)

    class Meta:
        model = Video
        fields = [
            "title",
            "description",
            "file",
            "photo",
            "tag_names",
        ]
        widgets = {
            "file": forms.FileInput(attrs={"accept": "video/*"}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            "content",
        ]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3}),
        }
