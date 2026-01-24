from django.urls import path
from . import views
from .views import my_qna_api, otherQna_roadmap

app_name = 'qna'

urlpatterns = [
    path("my/", views.qna_my_list, name="my_list"),
    path("user/<int:user_id>/", views.qna_user_list, name="user_qna"),
    path('write/', views.qna_write, name='write'),
    path('submit/', views.qna_submit, name='submit'),
    path('<int:qna_id>/', views.qna_detail, name='detail'),
    path('<int:qna_id>/answer/', views.answer_submit, name='answer'),
    path("api/my/", my_qna_api, name="api_my"),
    path("otherQna_roadmap/<int:user_id>/", otherQna_roadmap, name="otherQna_roadmap")    
]
