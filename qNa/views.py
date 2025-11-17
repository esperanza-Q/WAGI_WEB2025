from django.shortcuts import render
from .models import Qna

def qna_list(request):
     qnas = Qna.objects.all().order_by('-created_at')
     return render(request, "qna_list.html", {"qnas": qnas})
