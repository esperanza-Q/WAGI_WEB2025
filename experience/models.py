from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class ActivityCategory(models.TextChoices):
    CLUB = "club", "동아리"
    ACADEMIC = "academic", "학회"
    CONTEST = "contest", "공모전"
    INTERN = "intern", "인턴"

class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
    
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
    activity_period = models.CharField(
    max_length=30,
    verbose_name="활동 기간"
    )
    @property
    def like_count(self):
        return self.reviewlike_set.filter(is_agree=True).count()

    # created / updated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="reviews")

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"

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

class ReviewFile(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="files"
    )
    file = models.FileField(upload_to="review_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def is_image(self):
        return self.file.name.lower().endswith(
            (".jpg", ".jpeg", ".png", ".gif", ".webp")
        )
    def filename(self):
        return self.file.name.split("/")[-1]
    def __str__(self):
        return self.file.name

