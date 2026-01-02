from django.db import models
from django.conf import settings   # ⭐ User 연결은 settings.AUTH_USER_MODEL 로!

# =====================
#  카테고리
# =====================
class Category(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name


# =====================
#  태그
# =====================
class Tag(models.Model):
    tag_name = models.CharField(max_length=50)

    def __str__(self):
        return self.tag_name


# =====================
#  모집글
# =====================
class Recruit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,     # ⭐ 커스텀 유저 대응
        on_delete=models.CASCADE,
        related_name='recruits'
    )

    title = models.CharField(max_length=200)
    body = models.TextField()
    contact = models.CharField(max_length=100)
    deadline = models.DateTimeField()
    is_recruiting = models.BooleanField(default=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recruits'
    )

    college_id = models.IntegerField(null=True, blank=True)   # 단과대 ID 저장

    tags = models.ManyToManyField(
        'Tag',
        through='RecruitTag',
        related_name='recruits'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# =====================
#  모집글 이미지
# =====================
class RecruitImage(models.Model):
    recruit = models.ForeignKey(
        Recruit,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image_url = models.ImageField(upload_to='recruit/images/')
    created_at = models.DateTimeField(auto_now_add=True)

    college_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.recruit.title} 이미지"


# =====================
#  모집글-태그 연결 테이블
# =====================
class RecruitTag(models.Model):
    recruit = models.ForeignKey(Recruit, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    college_id = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('recruit', 'tag')   # 동일 태그 중복 X

    def __str__(self):
        return f"{self.recruit.title} - {self.tag.tag_name}"