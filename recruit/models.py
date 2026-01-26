from django.db import models
from django.conf import settings
from django.utils import timezone
from accounts.models import College
from datetime import date

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
    field = models.CharField(max_length=100, default='기탄')
    deadline = models.DateField()
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

    # ✅ 태그 (ERD 기준: Recruit ↔ Tag, 중간 테이블 사용)
    tags = models.ManyToManyField(
        Tag,
        through='RecruitTag',
        related_name='recruits'
    )

    # ✅ deadline 지나면 자동 모집 종료
    def save(self, *args, **kwargs):
        if self.deadline < timezone.localdate():
            self.is_recruiting = False
        super().save(*args, **kwargs)

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
    
    @property
    def is_image(self):
        name = self.image_url.name.lower()
        return name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))

    def __str__(self):
        return f"Image for {self.recruit.title}"


# ✅ 모집글-태그 중간 테이블 (ERD 동일)
class RecruitTag(models.Model):
    TAG_TYPE_CHOICES = (
        ('FIELD', '모집분야'),
        ('HASHTAG', '해시태그'),
    )

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

    # 🔥 추가된 핵심 필드
    tag_type = models.CharField(
        max_length=10,
        choices=TAG_TYPE_CHOICES,
        default='HASHTAG'
    )

    class Meta:
        unique_together = ('tag', 'recruit', 'tag_type')

    def __str__(self):
        return f"{self.recruit.title} - {self.tag.tag_name} ({self.get_tag_type_display()})"


# ✅ 좋아요
class RecruitLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='liked_recruits'
    )
    recruit = models.ForeignKey(
        Recruit,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recruit')

    def __str__(self):
        return f'{self.user} ❤️ {self.recruit.title}'

def save(self, *args, **kwargs):
    if self.deadline and self.deadline < date.today():
        self.is_recruiting = False
    super().save(*args, **kwargs)

#댓글
class Comment(models.Model):
    recruit = models.ForeignKey(Recruit, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return self.content[:20]
    
class RecruitScrap(models.Model):
    recruit = models.ForeignKey(Recruit, on_delete=models.CASCADE, related_name="scrap")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    

