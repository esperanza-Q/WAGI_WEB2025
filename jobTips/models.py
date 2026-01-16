from django.db import models
from django.conf import settings

# Create your models here.
class JobTipPost(models.Model):
    class Category(models.TextChoices):
        RESUME = 'resume', '합격 자소서'
        INTERVIEW = 'interview', '면접 후기'
        PORTFOLIO = 'portfolio', '포트폴리오'

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobtip_posts'
    )

    category = models.CharField(max_length=20, choices=Category.choices, default=Category.RESUME)
    title = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    pass_info = models.CharField(max_length=120)

    content = models.TextField()  # 본문 + 팁 통합
    experience_tip = models.TextField(blank=True, verbose_name="개인 경험이나 팁")
    file_attachment = models.FileField(
        upload_to='jobtips/files/',
        blank=True,
        null=True
    )

    tags = models.CharField(max_length=200, blank=True)

    # 공감(좋아요) 필드
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='liked_jobtip_posts'
    )

    # ✅ 스크랩 필드 추가
    scraps = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='scrapped_jobtip_posts'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(
        'JobTipPost',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobtip_comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} - {self.content[:20]}'