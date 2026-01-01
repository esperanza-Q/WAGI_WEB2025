from django import forms
from .models import Review, ReviewImage, ActivityCategory

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
class ReviewForm(forms.ModelForm):
    GRADE_CHOICES = [
        ('1학년', '1학년'),
        ('2학년', '2학년'),
        ('3학년', '3학년'),
        ('4학년', '4학년'),
    ]
    YEAR_CHOICES = [(str(y), f"{y}년") for y in range(2020, 2031)]
    TERM_CHOICES = [
        ('1학기', '1학기'),
        ('2학기', '2학기'),
        ('여름방학', '여름방학'),
        ('겨울방학', '겨울방학'),
    ]
    grade = forms.ChoiceField(choices=GRADE_CHOICES, label='학년')
    year = forms.ChoiceField(choices=YEAR_CHOICES, label='연도')
    term = forms.ChoiceField(choices=TERM_CHOICES, label='학기')
    class Meta:
        model = Review
        fields = ['category', 'title', 'content', 'rating', 'grade', 'year', 'term']
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

class ReviewImageForm(forms.ModelForm):
    class Meta:
        model = ReviewImage
        fields = ['image']
class ReviewImageMultipleForm(forms.Form):
    images = forms.FileField(
        widget=MultiFileInput(attrs={'multiple': True}),
        required=False
    )
class ReviewFileMultipleForm(forms.Form):
    files = forms.FileField(
        widget=MultiFileInput(attrs={'multiple': True}),
        required=False,
        label="첨부파일"
    )