from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class ActivityCategory(models.TextChoices):
    CLUB = "club", "동아리"
    ACADEMIC = "academic", "학회"
    CONTEST = "contest", "공모전"
    INTERN = "intern", "인턴"

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # 카테고리
    category = models.CharField(
        max_length=20,
        choices=ActivityCategory.choices
    )

    # 제목 = 활동 이름만
    title = models.CharField(max_length=100)

    # 본문
    content = models.TextField()

    # 별점
    rating = models.PositiveSmallIntegerField(default=5)

    # 경험자 인증
    is_verified = models.BooleanField(default=False)

    # 활동 당시 학년 (1~4)
    grade_at_time = models.PositiveSmallIntegerField()

    # created / updated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"
    
class ReviewLike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_agree = models.BooleanField()  # True=동의해요, False=동의하지 않아요

    class Meta:
        unique_together = ('review', 'user')  # 중복 방지