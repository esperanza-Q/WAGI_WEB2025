app_name = 'search'
from django.urls import path
from .views import search_reviews, search_reviews_page, search_expr_test, search_jobTips, search_recruit

urlpatterns = [
    path("reviews/", search_reviews, name="search-reviews"),
    path("reviews/test/", search_reviews_page, name="search-reviews-page"),
    path("expr/", search_expr_test, name="search-expr-test"),
    path('jobTips/', search_jobTips, name='search-jobTips'),
    path('recruit/', search_recruit, name='search-recruit'),
]