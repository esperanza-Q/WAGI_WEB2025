from django.contrib import admin
from .models import JobTipPost

@admin.register(JobTipPost)
class JobTipPostAdmin(admin.ModelAdmin):
    # 1. 목록 화면 설정
    list_display = ('title', 'category', 'author', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'content')

    # 2. 글쓰기/수정 화면 순서 (와이어프레임 12쪽 순서와 동일하게 배치)
    fields = [
        'author',           # 작성자
        'category',         # 자소서/면접/포폴 선택
        'title',            # 제목
        'position',         # 지원 분야(직무/포지션)
        'pass_info',        # 합격 연도와 전형 유형
        'content',          # 후기 본문
        'file_attachment',  # 파일 업로드 (중간으로 이동!)
        'experience_tip',   # 개인 경험이나 팁
        'tags',             # 태그 추가
        'likes',            # 좋아요 (어드민용)
    ]