from django.db import models
from django.conf import settings
from accounts.models import College

# ✅ 카테고리
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50)

    def __str__(self):
        return self.category_name

# ✅ 태그
class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    tag_name = models.CharField(max_length=50)

    def __str__(self):
        return self.tag_name

# ✅ 모집글
class Recruit(models.Model):
    recruit_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    body = models.TextField()
    contact = models.CharField(max_length=100)
    deadline = models.DateTimeField()
    is_recruiting = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 외래키
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recruits'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recruits'
    )
    college = models.ForeignKey(
        College,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recruits'
    )

    def __str__(self):
        return self.title

# ✅ 모집글 이미지
class RecruitImage(models.Model):
    image_id = models.AutoField(primary_key=True)
    image_url = models.ImageField(upload_to='recruit_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    # 외래키
    recruit = models.ForeignKey(
        Recruit,
        on_delete=models.CASCADE,
        related_name='images'
    )
    college = models.ForeignKey(
        College,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recruit_images'
    )

    def __str__(self):
        return f"Image for {self.recruit.title}"

# ✅ 모집글-태그 중간 테이블
class RecruitTag(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recruit_tags'
    )
    recruit = models.ForeignKey(
        Recruit,
        on_delete=models.CASCADE,
        related_name='recruit_tags'
    )
    college = models.ForeignKey(
        College,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recruit_tags'
    )

    class Meta:
        unique_together = ('tag', 'recruit')  # 중복 방지

    def __str__(self):
        return f"{self.recruit.title} - {self.tag.tag_name}"