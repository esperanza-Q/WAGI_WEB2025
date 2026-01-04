from django.shortcuts import render, get_object_or_404, redirect
from .models import Recruit, RecruitImage
import json

# 1. 모집글 목록 페이지 (b_list.html)
def recruit_list(request):
    recruits = Recruit.objects.all().order_by('-created_at')
    return render(request, 'b_list.html', {'recruits': recruits})


# 2. 모집글 상세 페이지 (b_detail.html)
def recruit_detail(request, recruit_id):
    recruit = get_object_or_404(Recruit, pk=recruit_id)
    images = recruit.images.all()
    return render(request, 'b_detail.html', {
        'recruit': recruit,
        'images': images,
    })


# 3. 모집글 작성 페이지 (b_post.html)
def recruit_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')  # 카테고리 ID 값
        field = request.POST.get('field')        # 분야 (필드명 명확히 확인)
        period = request.POST.get('period')      # 모집 기간
        description = request.POST.get('description')  # 본문
        link = request.POST.get('link')          # 연락 수단 (예: 오픈카톡 링크 등)
        tags = request.POST.get('tags')          # JSON 문자열 (예: '["tag1", "tag2"]')

        recruit = Recruit.objects.create(
            title=title,
            category_id=category,
            field=field,
            deadline=period,
            body=description,
            contact=link,
            tags=json.loads(tags) if tags else [],
            user=request.user,
            college=request.user.college,
        )

        # 첨부 이미지 저장
        for file in request.FILES.getlist('images'):
            RecruitImage.objects.create(recruit=recruit, image=file)

        return redirect('recruit_detail', recruit_id=recruit.recruit_id)

    return render(request, 'b_post.html')


# 4. 모집글 수정 페이지 (b_edit.html)
def recruit_edit(request, recruit_id):
    recruit = get_object_or_404(Recruit, pk=recruit_id)

    if request.method == 'POST':
        recruit.title = request.POST.get('title')
        recruit.category_id = request.POST.get('category')
        recruit.field = request.POST.get('field')
        recruit.deadline = request.POST.get('period')
        recruit.body = request.POST.get('description')
        recruit.contact = request.POST.get('link')
        tags = request.POST.get('tags')
        recruit.tags = json.loads(tags) if tags else []
        recruit.save()

        # 삭제된 이미지 처리
        deleted_files = json.loads(request.POST.get('deleted_files', '[]'))
        if deleted_files:
            RecruitImage.objects.filter(id__in=deleted_files, recruit=recruit).delete()

        # 새 이미지 추가
        for file in request.FILES.getlist('images'):
            RecruitImage.objects.create(recruit=recruit, image=file)

        return redirect('recruit_detail', recruit_id=recruit.recruit_id)

    return render(request, 'b_edit.html', {'recruit': recruit})
