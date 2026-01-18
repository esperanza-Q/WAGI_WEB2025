
from django.urls import path
from . import views

app_name = "career"

urlpatterns = [
    path("myroadmaphome", views.roadmap_home, name="roadmap_home"),
    path("myroadmap-post", views.roadmap_create_front, name="roadmap_create_front"),
    path("roadmap/<int:pk>/myroadmap-detail", views.roadmap_detail_front, name="roadmap_detail_front"),
    path("roadmap/<int:pk>/myroadmap-edit", views.roadmap_update_front, name="roadmap_update_front"),
    path("roadmap/<int:pk>/delete/", views.roadmap_delete, name="roadmap_delete"),
    path("myroadmap-detail", views.roadmap_detail_query, name="roadmap_detail_query"),
    # ✅ JS 호환용 (html → 공식 엔드포인트로 넘기기)
    path("myroadmap-detail.html", views.roadmap_detail_html_redirect),
]
