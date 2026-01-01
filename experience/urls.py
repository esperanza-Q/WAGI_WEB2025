from django.urls import path
from . import views

urlpatterns = [
    path('', views.review_list, name="review_list"),
    path('create/', views.review_create, name="review_create"),
    path('<int:review_id>/', views.review_detail, name="review_detail"),
    path("<int:review_id>/like/", views.toggle_like, name="toggle_like"),
    path("<int:review_id>/comment/", views.add_comment, name="add_comment"),
    path('<int:review_id>/edit/', views.review_edit, name='review_edit'),
    path('<int:review_id>/delete/', views.review_delete, name='review_delete'),
    path('image/<int:image_id>/delete/', views.delete_image, name='delete_image'),
    path("file/<int:file_id>/delete/", views.delete_file, name="delete_file"),
    path('<int:review_id>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('<int:review_id>/scrap/', views.toggle_scrap, name='toggle_scrap'),
]
