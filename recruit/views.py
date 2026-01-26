from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import json
from django.utils.timezone import now
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Recruit, RecruitLike, RecruitImage, RecruitTag, Category, Tag, Comment, RecruitScrap


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
        )
    elif status == 'closed':
        recruits = recruits.filter(
            is_recruiting=False
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
    
    is_scrapped = RecruitScrap.objects.filter(
        user=request.user,
        recruit=recruit
    ).exists()  # 스크랩이 존재하면 True, 없으면 False

    return render(request, 'recruit-detail.html', {
        'recruit': recruit,
        'images': images,
        'comments': parent_comments,
        'reply_map': reply_map,
        'tags': tags,
        'is_scrapped' : is_scrapped
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
        for file in request.FILES.getlist('new_images'):
            RecruitImage.objects.create(
                recruit=recruit,
                image_url=file,
                college=None
            )

        return redirect('recruit:recruit_detail', recruit_id=recruit.recruit_id)

    # images = RecruitImage.objects.filter(recruit_id=recruit_id)
    # print("이미지객체", images)

    # # GET 요청
    # return render(request, 'recruit-edit.html', {
    #     'recruit': recruit,
    #     'categories': Category.objects.all(),
    #     'images':images
    # })
    # ===== 🔥 GET 요청 수정 부분 (기존 파일 데이터를 JS용 JSON으로 변환) =====
    images = RecruitImage.objects.filter(recruit_id=recruit_id)
    print("이미지객체", images)
    
    # 🔥 추가: 기존 이미지를 JS가 이해할 수 있는 형식으로 변환
    existing_files = []
    for img in images:
        existing_files.append({
            'id': img.image_id,  # 삭제 시 필요한 ID
            'name': img.image_url.name.split('/')[-1] if img.image_url.name else 'image.jpg',  # 파일명 추출
            'url': img.image_url.url,  # 이미지 URL
            'type': 'image'  # 이미지 타입
        })
    
    # 🔥 추가: 태그도 JSON 형식으로 변환
    tags_list = [tag.tag_name for tag in recruit.tags.all()]

    # GET 요청
    return render(request, 'recruit-edit.html', {
        'recruit': recruit,
        'categories': Category.objects.all(),
        'images': images,
        'existing_files_json': json.dumps(existing_files),  # 🔥 추가
        'tags_json': json.dumps(tags_list)  # 🔥 추가
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


@login_required
def recruit_scrap(request, recruit_id):
    print("request.method : ", request.method)
    if request.method=='POST':
        # 🔥 수정: get_object_or_404로 게시글 존재 확인
        recruit = get_object_or_404(Recruit, recruit_id=recruit_id)
        print("recruit:", recruit)
        
        # 🔥 수정: filter()로 현재 사용자의 스크랩 찾기 (exists()는 True/False만 반환)
        scrap = RecruitScrap.objects.filter(
            user=request.user,  # 🔥 추가: 현재 사용자 기준
            recruit=recruit
        ).first()
        
        print("🔥🔥🔥🔥", scrap)
        
        # 🔥 수정: 스크랩이 있으면 삭제, 없으면 생성 (토글)
        if scrap:
            scrap.delete()  # 🔥 수정: remove()가 아니라 delete()
            is_scrapped=False
        else:
            RecruitScrap.objects.create(
                user=request.user,
                recruit=recruit
            )
            is_scrapped=True

    return redirect('recruit:recruit_detail',  recruit_id=recruit_id)