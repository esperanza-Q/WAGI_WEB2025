from django import forms
from .models import Review, ActivityCategory

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
class ReviewForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        label="태그",
        help_text="쉼표(,)로 구분해서 입력하세요"
    )
    activity_period = forms.CharField()
    class Meta:
        model = Review
        fields = ['category', 'title', 'content', 'rating', 'activity_period']
        labels = {
            'category': '활동 카테고리 선택',
            'title': '제목',
            'content': '후기 본문',
            'rating': '별점',
        }
        widgets = {
            'category': forms.RadioSelect(choices=ActivityCategory.choices),
            'content': forms.Textarea(attrs={'rows': 5}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
class ReviewFileMultipleForm(forms.Form):
    files = forms.FileField(
        required=False,
        widget=MultiFileInput(),
        label="첨부파일"
    )