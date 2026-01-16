from django import forms
from .models import JobTipPost


class JobTipPostForm(forms.ModelForm):
    class Meta:
        model = JobTipPost
        fields = [
            "title", "category", "position", "pass_info",
            "content", "file_attachment", "experience_tip", "tags"
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "jobtips-post-input"}),
            "position": forms.TextInput(attrs={"class": "jobtips-post-input"}),
            "pass_info": forms.TextInput(attrs={"class": "jobtips-post-input"}),
            "content": forms.Textarea(attrs={"class": "jobtips-post-textarea"}),
            "experience_tip": forms.Textarea(attrs={"class": "jobtips-post-textarea"}),
            # tags는 JS가 hidden에 넣을거라 화면 입력칸과 별개로 처리할거임
            "tags": forms.HiddenInput(),
        }
