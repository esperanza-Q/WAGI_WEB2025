from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['category', 'title', 'content', 'rating', 'grade_at_time']
        labels = {
            'category': '카테고리',
            'title': '제목',
            'content': '내용',
            'rating': '별점',
            'grade_at_time': '활동 학기',
        }
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'grade_at_time': forms.NumberInput(attrs={'min': 1, 'max': 8}),
        }
