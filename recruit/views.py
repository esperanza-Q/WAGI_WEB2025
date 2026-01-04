from django.shortcuts import render, get_object_or_404, redirect
from .models import Recruit, RecruitImage
import json

# 1. 모집글 목록 페이지 (b_list.html)
def recruit_list(request):
    # 🔹 쿼리 파라미터 가져오기
    category = request.GET.get('category')  # ex. '동아리', '공모전', '스터디'
    status = request.GET.get('status')      # 'open' or 'closed'
    order = request.GET.get('order', 'latest')  # 'latest'가 기본

    # 🔹 전체 모집글 가져오기
    recruits = Recruit.objects.all()

    # 🔹 필터: 카테고리
    if category in ['동아리', '공모전', '스터디']:
        recruits = recruits.filter(category__name=category)

    # 🔹 필터: 모집 상태 (is_recruiting)
    if status == 'open':
        recruits = recruits.filter(is_recruiting=True)
    elif status == 'closed':
        recruits = recruits.filter(is_recruiting=False)

    # 🔹 정렬: 최신순
    if order == 'latest':
        recruits = recruits.order_by('-created_at')

    return render(request, 'b_list.html', {
        'recruits': recruits,
        'selected_category': category,
        'selected_status': status,
        'selected_order': order,
    })


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
        category = request.POST.get('category')  # 카테고리 ID
        field = request.POST.get('field')        # 모집 분야
        period = request.POST.get('period')      # 모집 기간 (마감일)
        description = request.POST.get('description')
        link = request.POST.get('link')
        tags = request.POST.get('tags')

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

        # 삭제된 이미지
        deleted_files = json.loads(request.POST.get('deleted_files', '[]'))
        if deleted_files:
            RecruitImage.objects.filter(id__in=deleted_files, recruit=recruit).delete()

        # 새 이미지 추가
        for file in request.FILES.getlist('images'):
            RecruitImage.objects.create(recruit=recruit, image=file)

        return redirect('recruit_detail', recruit_id=recruit.recruit_id)

    return render(request, 'b_edit.html', {'recruit': recruit})
