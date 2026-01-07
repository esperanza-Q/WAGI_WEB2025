from django.db import models
from django.conf import settings
import re  # ✅ [추가] 시작 연도 파싱용


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

    # ✅ [수정] 기간을 텍스트로 저장 (예: "2024.03 - 2024.11")
    # ✅ period_text 삭제 요구사항 반영: date가 그 역할을 수행
    date = models.CharField(
        max_length=50,
        null=False,
        blank=False
    )

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
        # ✅ [수정] date는 문자열이므로 정렬 안정성 위해 -id 우선 권장
        ordering = ['-id']

    def __str__(self):
        return f'{self.title} ({self.date})'

    @property
    def year(self):
        """
        ✅ [수정] date가 문자열이므로 시작 연도를 파싱해서 반환
        예: "2024.01 - 2025.01" -> 2024
        """
        m = re.search(r"(19|20)\d{2}", self.date or "")
        return int(m.group()) if m else 0
