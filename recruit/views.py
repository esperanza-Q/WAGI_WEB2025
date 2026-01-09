from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import json

from .models import Recruit, RecruitImage, RecruitTag, Category, Tag, Comment


# =========================
# 1. 모집글 목록 페이지
# =========================
def recruit_list(request):
    category = request.GET.get('category')
    status = request.GET.get('status')
    order = request.GET.get('order')

    recruits = Recruit.objects.annotate(
        like_count=Count('likes')
    )

    # 카테고리 필터
    if category in ['동아리', '공모전', '스터디']:
        recruits = recruits.filter(category__category_name=category)

    # 모집 상태 필터 (status 값 있을 때만)
    if status == 'open':
        recruits = recruits.filter(is_recruiting=True)
    elif status == 'closed':
        recruits = recruits.filter(is_recruiting=False)
    # else: 전체 → 필터 안 함

    # 정렬 (기본은 최신순)
    if order == 'latest' or order is None:
        recruits = recruits.order_by('-created_at')
    else:
        recruits = recruits.order_by('-like_count')

    return render(request, 'b_list.html', {
        'recruits': recruits,
        'selected_category': category,
        'selected_status': status,
        'selected_order': order,
    })

# =========================
# 2. 모집글 작성
# =========================
@login_required
def recruit_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')

        category_name = request.POST.get('category')
        category = get_object_or_404(Category, category_name=category_name)

        deadline_str = request.POST.get('deadline')
        body = request.POST.get('body')
        contact = request.POST.get('contact')
        tags = request.POST.get('tags')

        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()

        recruit = Recruit.objects.create(
            title=title,
            category=category,
            deadline=deadline,
            body=body,
            contact=contact,
            user=request.user,
            college=None,
        )

        # 🔥 태그 저장 (이미 잘 되어 있음)
        if tags:
            tag_names = json.loads(tags)
            for tag_name in tag_names:
                tag_obj, _ = Tag.objects.get_or_create(tag_name=tag_name)
                RecruitTag.objects.get_or_create(
                    recruit=recruit,
                    tag=tag_obj,
                    college=None
                )

        # 이미지 저장
        for file in request.FILES.getlist('images'):
            RecruitImage.objects.create(
                recruit=recruit,
                image_url=file,
                college=None
            )

        return redirect('recruit_detail', recruit_id=recruit.recruit_id)

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

    comments = Comment.objects.filter(
        recruit=recruit
    ).select_related('user').order_by('created_at')

    parent_comments = comments.filter(parent__isnull=True)
    reply_map = {
        parent.id: comments.filter(parent=parent)
        for parent in parent_comments
    }

    # 🔥🔥🔥 핵심 추가: 태그 조회
    tags = RecruitTag.objects.filter(
        recruit=recruit
    ).select_related('tag')

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        content = request.POST.get("content", "").strip()
        parent_id = request.POST.get("parent_id")

        if content:
            Comment.objects.create(
                recruit=recruit,
                user=request.user,
                content=content,
                parent_id=parent_id if parent_id else None
            )
            return redirect('recruit_detail', recruit_id=recruit_id)

    return render(request, 'b_detail.html', {
        'recruit': recruit,
        'images': images,
        'comments': parent_comments,
        'reply_map': reply_map,
        'tags': tags,  # ✅ 여기만 추가
    })


# =========================
# 4. 댓글 삭제
# =========================
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user != request.user:
        return HttpResponseForbidden("댓글을 삭제할 수 없습니다.")

    recruit_id = comment.recruit.recruit_id
    comment.delete()
    return redirect('recruit_detail', recruit_id=recruit_id)


# =========================
# 5. 모집글 수정
# =========================
@login_required
def recruit_edit(request, recruit_id):
    recruit = get_object_or_404(Recruit, recruit_id=recruit_id)

    if recruit.user != request.user:
        return HttpResponseForbidden("수정 권한이 없습니다.")

    if request.method == 'POST':
        recruit.title = request.POST.get('title')

        category_name = request.POST.get('category')
        recruit.category = get_object_or_404(Category, category_name=category_name)

        recruit.deadline = datetime.strptime(
            request.POST.get('deadline'), "%Y-%m-%d"
        ).date()

        recruit.body = request.POST.get('body')
        recruit.contact = request.POST.get('contact')
        recruit.save()

        tags = request.POST.get('tags')
        if tags:
            tag_names = json.loads(tags)
            RecruitTag.objects.filter(recruit=recruit).delete()
            for tag_name in tag_names:
                tag_obj, _ = Tag.objects.get_or_create(tag_name=tag_name)
                RecruitTag.objects.create(
                    recruit=recruit,
                    tag=tag_obj,
                    college=None
                )

        deleted_files = json.loads(request.POST.get('deleted_files', '[]'))
        RecruitImage.objects.filter(
            id__in=deleted_files,
            recruit=recruit
        ).delete()

        for file in request.FILES.getlist('images'):
            RecruitImage.objects.create(
                recruit=recruit,
                image_url=file,
                college=None
            )

        return redirect('recruit_detail', recruit_id=recruit.recruit_id)

    return render(request, 'b_edit.html', {
        'recruit': recruit,
        'categories': Category.objects.all(),
    })


# =========================
# 6. 모집글 삭제
# =========================
'''@login_required
def recruit_delete(request, recruit_id):
    recruit = get_object_or_404(Recruit, recruit_id=recruit_id)

    if recruit.user != request.user:
        return HttpResponseForbidden("삭제 권한이 없습니다.")

    recruit.delete()
    return redirect('recruit_list')
'''