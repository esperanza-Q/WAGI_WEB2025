from django import forms
from .models import Recruit

class RecruitForm(forms.ModelForm):
    class Meta:
        model = Recruit
        fields = ['title', 'category', 'field', 'period', 'description', 'link', 'tags']