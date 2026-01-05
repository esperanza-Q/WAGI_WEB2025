from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from .models import Recruit, RecruitImage, RecruitTag, Category, Tag
import json


# =========================
# 1. 모집글 목록 페이지
# =========================
def recruit_list(request):
    category = request.GET.get('category')   # 동아리 / 공모전 / 스터디
    status = request.GET.get('status')       # open / closed
    order = request.GET.get('order')         # latest

    recruits = Recruit.objects.annotate(
        like_count=Count('likes')
    )

    # ------- 카테고리 필터 -------
    if category in ['동아리', '공모전', '스터디']:
        recruits = recruits.filter(category__category_name=category)

    # ------- 모집 상태 필터 -------
    if status == 'open':
        recruits = recruits.filter(is_recruiting=True)
    elif status == 'closed':
        recruits = recruits.filter(is_recruiting=False)

    # ------- 최신순 정렬 -------
    if order == 'latest':
        recruits = recruits.order_by('-created_at')
    else:
        recruits = recruits.order_by('-created_at')  # 기본 최신순

    return render(request, 'b_list.html', {
        'recruits': recruits,
        'selected_category': category,
        'selected_status': status,
        'selected_order': order,
    })


# =========================
# 2. 모집글 작성
# =========================
def recruit_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')

        category_id = request.POST.get('category')
        category = get_object_or_404(Category, pk=category_id)

        deadline_str = request.POST.get('deadline')
        description = request.POST.get('description')
        link = request.POST.get('link')
        tags = request.POST.get('tags')

        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()

        recruit = Recruit.objects.create(
            title=title,
            category=category,        # ✅ FK는 객체로
            deadline=deadline,
            body=description,
            contact=link,
            user=request.user,
            college=None,             # 임시 유지
        )

        # 태그
        if tags:
            tag_names = json.loads(tags)  # 예: ["AI", "디자인", "프론트엔드"]
            for tag_name in tag_names:
                tag_obj, _ = Tag.objects.get_or_create(tag_name=tag_name)
                RecruitTag.objects.get_or_create(
                    recruit=recruit,
                    tag=tag_obj,
                    college=None  # 필요 시 college도 처리
                )

        # 이미지
        for file in request.FILES.getlist('images'):
            RecruitImage.objects.create(
                recruit=recruit,
                image_url=file,
                college=None
            )

        return redirect('recruit_detail', recruit_id=recruit.recruit_id)

    # 🔥 GET 요청 시 카테고리 내려주기 (필수)
    return render(request, 'b_post.html', {
        'categories': Category.objects.all()
    })


# =========================
# 3. 모집글 상세 페이지
# =========================
def recruit_detail(request, recruit_id):
    recruit = get_object_or_404(
        Recruit.objects.annotate(like_count=Count('likes')),
        recruit_id=recruit_id
    )

    images = recruit.images.all()

    return render(request, 'b_detail.html', {
        'recruit': recruit,
        'images': images,
    })


# =========================
# 4. 모집글 수정 페이지
# =========================
def recruit_edit(request, recruit_id):
    recruit = get_object_or_404(Recruit, pk=recruit_id)

    if request.method == 'POST':
        recruit.title = request.POST.get('title')

        category_id = request.POST.get('category')
        recruit.category = get_object_or_404(Category, pk=category_id)  # ✅ 안전

        deadline_str = request.POST.get('deadline')
        recruit.deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()

        recruit.body = request.POST.get('description')
        recruit.contact = request.POST.get('link')
        recruit.save()

        # 태그 수정 (전부 삭제 후 재생성)
        RecruitTag.objects.filter(recruit=recruit).delete()
        tags = request.POST.get('tags')
        if tags:
            tag_ids = json.loads(tags)
            for tag_id in tag_ids:
                RecruitTag.objects.create(
                    recruit=recruit,
                    tag_id=tag_id,
                    college=None
                )

        # 삭제된 이미지
        deleted_files = json.loads(request.POST.get('deleted_files', '[]'))
        if deleted_files:
            RecruitImage.objects.filter(
                id__in=deleted_files,
                recruit=recruit
            ).delete()

        # 새 이미지 추가
        for file in request.FILES.getlist('images'):
            RecruitImage.objects.create(
                recruit=recruit,
                image_url=file,
                college=None
            )

        return redirect('recruit_detail', recruit_id=recruit.recruit_id)

    # 🔥 수정 페이지에서도 카테고리 필요
    return render(request, 'b_edit.html', {
        'recruit': recruit,
        'categories': Category.objects.all()
    })
