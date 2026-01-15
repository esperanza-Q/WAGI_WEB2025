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
    category = models.CharField(
        max_length=20,
        choices=ActivityCategory.choices
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    is_verified = models.BooleanField(default=False)
    #활동기간
    grade = models.CharField(max_length=10, default="1학년")
    year = models.CharField(max_length=4, default="2025")
    term = models.CharField(max_length=20, default="1학기")
    year_term = models.CharField(max_length=30, editable=False, default="")
    @property
    def like_count(self):
        return self.reviewlike_set.filter(is_agree=True).count()

    def save(self, *args, **kwargs):
        self.year_term = f"{self.year} {self.testerm}"
        super().save(*args, **kwargs)

    # created / updated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"

class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="review_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.review.title}"

class ReviewLike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_agree = models.BooleanField(default=False)  # True=좋아요

    class Meta:
        unique_together = ('review', 'user')  # 중복 방지
        
class ReviewComment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.display_name}: {self.content[:20]}"

class ReviewScrap(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="scraps")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')  # 중복 스크랩 방지

    def __str__(self):
        return f"{self.user.username} → {self.review.title}"
