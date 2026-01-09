from django.urls import path
from . import views

urlpatterns = [
    path('post/', views.recruit_post, name='recruit_post'),  
    path('list/', views.recruit_list, name='recruit_list'),        
    path('detail/<int:recruit_id>/', views.recruit_detail, name='recruit_detail'),
    path('edit/<int:recruit_id>/', views.recruit_edit, name='recruit_edit'), 
    path('recruit/<int:recruit_id>/delete/', views.recruit_delete, name='recruit_delete'),
    path('comment/<int:comment_id>/edit/', views.comment_edit, name='comment_edit'),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
]