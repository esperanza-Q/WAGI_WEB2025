from django.urls import path
from . import views

app_name = 'recruit'

urlpatterns = [
    # 모집글 관련
    path('list/', views.recruit_list, name='recruit_list'),
    path('post/', views.recruit_post, name='recruit_post'),
    path('detail/<int:recruit_id>/', views.recruit_detail, name='recruit_detail'),
    path('edit/<int:recruit_id>/', views.recruit_edit, name='recruit_edit'),
    path('delete/<int:recruit_id>/', views.recruit_delete, name='recruit_delete'),

    # 좋아요 기능
    path('like/<int:recruit_id>/', views.recruit_like, name='recruit_like'),

    # 댓글 관련
    path('comment/<int:comment_id>/edit/', views.comment_edit, name='comment_edit'),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('detail/<int:recruit_id>/comment/<int:comment_id>/reply/', views.comment_reply, name='comment_reply'),
]