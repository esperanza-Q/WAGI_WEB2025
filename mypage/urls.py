from django.urls import path
from mypage.views import mypage_home

app_name='mypage'

urlpatterns = [
    path('', mypage_home, name='home')
]