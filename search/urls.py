from django.urls import path
from .views import search_reviews

urlpatterns = [
    path("reviews/", search_reviews, name="search-reviews"),
]