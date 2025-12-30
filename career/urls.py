
from django.urls import path
from . import views

app_name = 'career'

urlpatterns = [
    path('roadmap/', views.roadmap_list, name='roadmap_list'),
    path('roadmap/new/', views.roadmap_create, name='roadmap_create'),
    path('roadmap/<int:pk>/', views.roadmap_detail, name='roadmap_detail'),
    path('roadmap/<int:pk>/edit/', views.roadmap_update, name='roadmap_update'),
    path('roadmap/<int:pk>/delete/', views.roadmap_delete, name='roadmap_delete'),
]
