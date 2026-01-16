from django.shortcuts import render

# Create your views here.
def mypage_home(request):
    return render(request, 'b_mypage.html')