from django import forms
from .models import CareerSharePost

# career/forms.py
class CareerShareForm(forms.ModelForm):
    class Meta:
        model = CareerShare
        fields = [
            'title', 'category', 'field', 'year_type',
            'content', 'image', 'rating', 'tags'
        ]
