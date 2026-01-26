from django import forms
from .models import Recruit, RecruitImage, Tag, RecruitTag

class RecruitForm(forms.ModelForm):
    class Meta:
        model = Recruit
        fields = ['title', 'body', 'contact', 'deadline', 'category']

class RecruitImageForm(forms.ModelForm):
    class Meta:
        model = RecruitImage
        fields = ['image_url']

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['tag_name']

class RecruitTagForm(forms.ModelForm):
    class Meta:
        model = RecruitTag
        fields = ['tag', 'recruit']
