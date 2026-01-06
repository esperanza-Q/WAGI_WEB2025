from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from .models import Recruit, RecruitImage, RecruitTag, Category, Tag, Comment
import json
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseForbidden


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
    comments = Comment.objects.filter(recruit=recruit).select_related('user').order_by('created_at')

    # 댓글 트리 구성
    parent_comments = comments.filter(parent__isnull=True)
    reply_map = {}
    for parent in parent_comments:
        reply_map[parent.id] = comments.filter(parent=parent)

    # 댓글 작성
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        content = request.POST.get("content", "").strip()
        parent_id = request.POST.get("parent_id")  # 대댓글 작성 시

        if content:
            comment = Comment.objects.create(
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
    })

# =========================
# 댓글 삭제
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
# 4. 모집글 수정
# =========================
@login_required
def recruit_edit(request, recruit_id):
    recruit = get_object_or_404(Recruit, pk=recruit_id)

    # 본인 글만 수정 가능
    if recruit.user != request.user:
        return HttpResponseForbidden("수정 권한이 없습니다.")

    if request.method == 'POST':
        recruit.title = request.POST.get('title')
        recruit.category = get_object_or_404(Category, pk=request.POST.get('category'))
        recruit.deadline = datetime.strptime(request.POST.get('deadline'), "%Y-%m-%d").date()
        recruit.body = request.POST.get('description')
        recruit.contact = request.POST.get('link')
        recruit.save()

        # 태그 수정
        RecruitTag.objects.filter(recruit=recruit).delete()
        tags = request.POST.get('tags')
        if tags:
            for tag_id in json.loads(tags):
                RecruitTag.objects.create(recruit=recruit, tag_id=tag_id, college=None)

        # 이미지 삭제
        deleted_files = json.loads(request.POST.get('deleted_files', '[]'))
        RecruitImage.objects.filter(id__in=deleted_files, recruit=recruit).delete()

        # 새 이미지 추가
        for file in request.FILES.getlist('images'):
            RecruitImage.objects.create(recruit=recruit, image_url=file, college=None)

        return redirect('recruit_detail', recruit_id=recruit.recruit_id)

    return render(request, 'recruit/b_edit.html', {
        'recruit': recruit,
        'categories': Category.objects.all(),
    })

# =========================
# 모집글 삭제
# =========================
@login_required
def recruit_delete(request, recruit_id):
    recruit = get_object_or_404(Recruit, pk=recruit_id)
    if recruit.user != request.user:
        return HttpResponseForbidden("삭제 권한이 없습니다.")
    recruit.delete()
    return redirect('recruit_list')  # 목록 페이지로 이동

