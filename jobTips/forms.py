from django import forms
from .models import JobTipPost

class JobTipPostForm(forms.ModelForm):
    class Meta:
        model = JobTipPost
        #모델(JobTipPost)에 있는 필드들을 모두 나열합니다.
        fields = [
            'category',
            'title',
            'position',
            'pass_info',
            'content',
            'experience_tip',
            'file_attachment',
            'tags',
        ]
