from django.urls import path
from . import views

app_name = 'jobTips'

urlpatterns = [
    path('', views.post_list, name='list'),
    path('create/', views.post_create, name='create'),
    path('<int:pk>/', views.post_detail, name='detail'),
    path('<int:pk>/like/', views.post_like, name='like'),
    
    # ✅ 스크랩 주소 추가
    path('<int:pk>/scrap/', views.post_scrap, name='post_scrap'),

    path('<int:pk>/edit/', views.post_edit, name='edit'),
    
   
    path('<int:pk>/delete/', views.post_delete, name='delete'),
    
    path("<int:pk>/comments/create/", views.comment_create, name="comment_create"),
    path("<int:pk>/comments/<int:comment_id>/delete/", views.comment_delete, name="comment_delete"),
]