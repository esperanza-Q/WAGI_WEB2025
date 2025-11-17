from django.urls import path
from . import views

urlpatterns = [
    path('', views.review_list, name="review_list"),
    path('create/', views.review_create, name="review_create"),
    path('<int:review_id>/', views.review_detail, name="review_detail"),
    path('<int:review_id>/like/<int:value>/', views.review_like, name="review_like"),
]
