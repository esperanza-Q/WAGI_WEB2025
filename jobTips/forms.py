from django import forms
from .models import JobTipPost


class JobTipPostForm(forms.ModelForm):
    class Meta:
        model = JobTipPost
        fields = [
            "title", "category", "position", "pass_info",
            "content", "experience_tip", "tags"
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "jobtips-post-input"}),
            "position": forms.TextInput(attrs={"class": "jobtips-post-input"}),
            "pass_info": forms.TextInput(attrs={"class": "jobtips-post-input"}),
            "content": forms.Textarea(attrs={"class": "jobtips-post-textarea"}),
            "experience_tip": forms.Textarea(attrs={"class": "jobtips-post-textarea"}),

            # tags는 프론트 JS가 hidden(name="tags")에 넣어서 보내는 값 그대로 받기
            "tags": forms.HiddenInput(),
        }
