from django.urls import path
from . import views

urlpatterns = [
    path('post/', views.recruit_post, name='recruit_post'),  
    path('list/', views.recruit_list, name='recruit_list'),        
    path('detail/<int:recruit_id>/', views.recruit_detail, name='recruit_detail'),
    path('edit/<int:recruit_id>/', views.recruit_edit, name='recruit_edit'),  
    path('delete/<int:recruit_id>/', views.recruit_delete, name='recruit_delete'),  

]