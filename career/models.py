from django.db import models
from django.conf import settings


class RoadmapEntry(models.Model):
    class Category(models.TextChoices):
        CLUB = 'club', '동아리'
        ACADEMIC = 'academic', '학회'
        CONTEST = 'contest', '공모전'
        INTERN = 'intern', '인턴'
        OTHER = 'other', '기타'

    # 작성자
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='roadmap_entries'
    )

    # 제목
    title = models.CharField(max_length=100)

    # 카테고리
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER
    )

    # 날짜(YYYY-MM-DD)
    date = models.DateField()

    # 기간을 텍스트로 쓰고 싶을 때 (예: 2025-1학기) – 선택사항
    period_text = models.CharField(max_length=50, blank=True)

    # 본문(활동 소개)
    description = models.TextField(blank=True)

    # 이미지 업로드
    image = models.ImageField(
        upload_to='roadmap/images/',
        blank=True,
        null=True
    )

    # 파일 업로드(증빙 자료 등)
    attachment = models.FileField(
        upload_to='roadmap/files/',
        blank=True,
        null=True
    )

    # 태그 (쉼표로 구분해서 입력)
    tags = models.CharField(max_length=100, blank=True)

    # 자동 시간 기록
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-id']  # 최근 날짜가 위로 오도록

    def __str__(self):
        return f'{self.title} ({self.date})'

    @property
    def year(self):
        return self.date.year
