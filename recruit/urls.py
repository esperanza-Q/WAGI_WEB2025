from django.urls import path
from . import views

urlpatterns = [
    path('post/', views.recruit_post, name='recruit_post'),   # b_post.html
    path('list/', views.recruit_list, name='recruit_list'),         # b_list.html
    path('detail/', views.recruit_detail, name='recruit_detail'),   # b_detail.html
    path('edit/', views.recruit_edit, name='recruit_edit'),         # b_edit.html
]