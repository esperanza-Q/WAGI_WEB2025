app_name = 'search'
from django.urls import path
from .views import search_reviews, search_reviews_page, search_expr_test

urlpatterns = [
    path("reviews/", search_reviews, name="search-reviews"),
    path("reviews/test/", search_reviews_page, name="search-reviews-page"),
    path("expr/", search_expr_test, name="search-expr-test"),
    # path('career/', career_review_list, name='career-review-list'),
    # path('recruit/', recruit_post_list, name='recruit-post-list'),
    
]