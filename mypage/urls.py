from django.urls import path
from mypage.views import mypage_home, scrap_list, my_post_list, profile_update, mypage_home_sent

app_name='mypage'

urlpatterns = [
    path('', mypage_home, name='home'),
    path('mypage_home_sent/', mypage_home_sent, name='sent'),
    path('scrap_list/<str:category>', scrap_list, name='scrap_list' ),
    path('my_post_list/<str:category>', my_post_list, name='my_post_list'),
    path('profile_update/', profile_update, name='profile_update')
    
]