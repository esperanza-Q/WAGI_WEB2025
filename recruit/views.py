from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import json
from django.utils.timezone import now
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Recruit, RecruitLike, RecruitImage, RecruitTag, Category, Tag, Comment


# =========================
# 1. 모집글 목록 페이지
# =========================
def recruit_list(request):
    category = request.GET.get('category')
    status = request.GET.get('status')
    order = request.GET.get('order')

    today = now().date()

    # 🔥 마감일 지난 모집글 상태 동기화
    Recruit.objects.filter(
        is_recruiting=True,
        deadline__lt=today
    ).update(is_recruiting=False)

    # ✅ 좋아요 수 + 댓글 수 annotate (여기만 추가)
    recruits = Recruit.objects.annotate(
        like_count=Count('likes', distinct=True),
        comment_count=Count('comments', distinct=True),
    )

    # 카테고리 필터
    if category in ['동아리', '공모전', '스터디']:
        recruits = recruits.filter(category__category_name=category)

    # 모집 상태 필터
    if status == 'open':
        recruits = recruits.filter(
            is_recruiting=True,
            deadline__gte=today
        )
    elif status == 'closed':
        recruits = recruits.filter(
            Q(is_recruiting=False) | Q(deadline__lt=today)
        )


    # =========================
    # 정렬 (🔥 최소 수정 핵심)
    # =========================
    if order == 'latest':
        # 최신순
        recruits = recruits.order_by('-created_at')
    else:
        # 기본 정렬:
        # 좋아요 ↓ → 댓글 ↓ → 최신순 ↓
        recruits = recruits.order_by(
            '-like_count',
            '-comment_count',
            '-created_at'
        )

    page = request.GET.get('page', '1')  
    paginator = Paginator(recruits, 10)  
    page_obj = paginator.get_page(page)

    return render(request, 'recruit-list.html', {
        'recruits': page_obj,
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
        field = request.POST.get('field'),
        tags = request.POST.get('tags')

        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()

        recruit = Recruit.objects.create(
            title=title,
            category=category,
            deadline=deadline,
            body=body,
            contact=contact,
            field=field,
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

        return redirect('recruit:recruit_detail', recruit_id=recruit.recruit_id)

    return render(request, 'recruit-post.html', {
        'categories': Category.objects.all()
    })


# =========================
# 3. 모집글 상세 페이지
# =========================
@login_required
def recruit_detail(request, recruit_id):
    recruit = get_object_or_404(
        Recruit.objects.annotate(like_count=Count('likes')),
        recruit_id=recruit_id
    )

    images = recruit.images.all().order_by('image_id')

    comments = Comment.objects.filter(
        recruit=recruit
    ).select_related('user').order_by('created_at')

    parent_comments = comments.filter(parent__isnull=True)

    reply_map = {
        parent.id: comments.filter(parent=parent)
        for parent in parent_comments
    }

    # ✅ 해시태그 조회만
    tags = RecruitTag.objects.filter(
        recruit=recruit
    ).select_related('tag')

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        parent_id = request.POST.get("parent_id")

        if content:
            Comment.objects.create(
                recruit=recruit,
                user=request.user,
                content=content,
                parent_id=parent_id if parent_id else None
            )

        return redirect('recruit:recruit_detail', recruit_id=recruit_id)

    return render(request, 'recruit-detail.html', {
        'recruit': recruit,
        'images': images,
        'comments': parent_comments,
        'reply_map': reply_map,
        'tags': tags,
    })

@login_required
def recruit_like(request, recruit_id):
    recruit = get_object_or_404(Recruit, recruit_id=recruit_id)

    like = RecruitLike.objects.filter(
        user=request.user,
        recruit=recruit
    )

    if like.exists():
        like.delete()
    else:
        RecruitLike.objects.create(
            user=request.user,
            recruit=recruit
        )

    return redirect('recruit:recruit_detail', recruit_id=recruit_id)

# =========================
# 4. 댓글 수정/삭제/답글
# =========================

# 댓글 수정
@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        return HttpResponseForbidden("권한이 없습니다.")

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            comment.content = content
            comment.save()

    return redirect('recruit:recruit_detail', recruit_id=comment.recruit.recruit_id)


# 댓글 삭제 (원댓글 및 답글 공통)
@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        return HttpResponseForbidden("권한이 없습니다.")

    recruit_id = comment.recruit.recruit_id
    comment.delete()

    return redirect('recruit:recruit_detail', recruit_id=recruit_id)


# ✅ 답글 등록 (추가된 부분)
@login_required
def comment_reply(request, recruit_id, comment_id):
    # 원댓글(부모 댓글)을 가져옵니다.
    parent_comment = get_object_or_404(Comment, id=comment_id)
    recruit = get_object_or_404(Recruit, recruit_id=recruit_id)

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Comment.objects.create(
                recruit=recruit,
                user=request.user,
                content=content,
                parent=parent_comment  # 부모 댓글을 지정하여 답글로 저장
            )

    return redirect('recruit:recruit_detail', recruit_id=recruit_id)


# =========================
# 5. 모집글 수정
# =========================
@login_required
def recruit_edit(request, recruit_id):
    recruit = get_object_or_404(Recruit, recruit_id=recruit_id)

    if recruit.user != request.user:
        return HttpResponseForbidden("수정 권한이 없습니다.")

    if request.method == 'POST':
        # 제목
        title = request.POST.get('title', '').strip()
        if not title:
            return render(request, 'recruit-edit.html', {
                'recruit': recruit,
                'categories': Category.objects.all(),
                'error': '제목은 필수 입력입니다.'
            })
        recruit.title = title

        # 카테고리
        category_name = request.POST.get('category')
        recruit.category = get_object_or_404(Category, category_name=category_name)

        # 날짜 (여러 포맷 허용)
        deadline_str = request.POST.get('deadline', '').strip()
        for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d"):
            try:
                recruit.deadline = datetime.strptime(deadline_str, fmt).date()
                break
            except ValueError:
                continue

        from django.utils import timezone
        recruit.is_recruiting = recruit.deadline >= timezone.now().date()

        recruit.field = request.POST.get('field', '').strip()

        # 본문 / 연락처
        recruit.body = request.POST.get('body')
        recruit.contact = request.POST.get('contact')
        recruit.save()

        # 태그 처리
        tags = request.POST.get('tags')
        if tags:
            try:
                tag_names = json.loads(tags)
            except json.JSONDecodeError:
                tag_names = []

            RecruitTag.objects.filter(recruit=recruit).delete()
            for tag_name in tag_names:
                tag_obj, _ = Tag.objects.get_or_create(tag_name=tag_name)
                RecruitTag.objects.create(
                    recruit=recruit,
                    tag=tag_obj,
                    college=None
                )

        # ✅ 삭제된 파일 처리 (🔥 여기만 핵심 수정)
        try:
            deleted_files = json.loads(request.POST.get('deleted_files', '[]'))
        except json.JSONDecodeError:
            deleted_files = []

        # 숫자인 image_id만 추출
        deleted_ids = []
        for item in deleted_files:
            try:
                deleted_ids.append(int(item))
            except (ValueError, TypeError):
                pass  # 'sample-img.png' 같은 값은 무시

        if deleted_ids:
            RecruitImage.objects.filter(
                image_id__in=deleted_ids,
                recruit=recruit
            ).delete()

        # 새 파일 업로드
        for file in request.FILES.getlist('files'):
            RecruitImage.objects.create(
                recruit=recruit,
                image_url=file,
                college=None
            )

        return redirect('recruit:recruit_detail', recruit_id=recruit.recruit_id)

    # GET 요청
    return render(request, 'recruit-edit.html', {
        'recruit': recruit,
        'categories': Category.objects.all(),
    })


# =========================
# 6. 모집글 삭제
# =========================
@login_required
def recruit_delete(request, recruit_id):
    recruit = get_object_or_404(Recruit, recruit_id=recruit_id)

    # 작성자 본인만 삭제 가능
    if request.user != recruit.user:
        return redirect('recruit:recruit_detail', recruit_id=recruit_id)

    if request.method == "POST":
        recruit.delete()
        return redirect('recruit:recruit_list')  # 삭제 후 목록 페이지로 이동

    return redirect('recruit:recruit_detail', recruit_id=recruit_id)