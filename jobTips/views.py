import json

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse

from .models import JobTipPost, Comment
from .forms import JobTipPostForm


# 카테고리/정렬 허용값
VALID_CATEGORIES = {"resume", "interview", "portfolio"}
VALID_SORT = {"latest", "likes"}


def post_list(request):
    q = request.GET.get("q", "").strip()[:100]
    category = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "latest").strip()

    if sort not in VALID_SORT:
        sort = "latest"
    if category and category not in VALID_CATEGORIES:
        category = ""

    posts = (
        JobTipPost.objects
        .select_related("author")
        .annotate(like_count=Count("likes", distinct=True))
    )

    if q:
        posts = posts.filter(title__icontains=q)
    if category:
        posts = posts.filter(category=category)

    if sort == "likes":
        posts = posts.order_by("-like_count", "-created_at")
    else:
        posts = posts.order_by("-created_at")

    return render(request, "jobTips/b_list.html", {
        "posts": posts,
        "q": q,
        "category": category,
        "sort": sort,
    })


def post_detail(request, pk):
    post = get_object_or_404(
        JobTipPost.objects
        .select_related("author")
        .annotate(like_count=Count("likes", distinct=True)),
        pk=pk
    )

    is_liked = (
        post.likes.filter(pk=request.user.pk).exists()
        if request.user.is_authenticated else False
    )

    # "아이유, 졸려" -> ["아이유", "졸려"]
    tags_list = [t.strip() for t in (post.tags or "").split(",") if t.strip()]

    # ✅ 댓글들: related_name='comments' 덕분에 바로 가져올 수 있음
    comments = post.comments.select_related("author").all()

    return render(request, "jobTips/b_detail.html", {
        "post": post,
        "is_liked": is_liked,
        "tags_list": tags_list,
        "is_scrapped": False,  # 스크랩 미구현이면 일단 False 고정
        "comments": comments,  # ✅ 템플릿에서 댓글 렌더링용
    })


@require_POST
@login_required
def post_like(request, pk):
    post = get_object_or_404(JobTipPost, pk=pk)

    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    # ✅ 너 urls.py에서 detail name이 'detail'이니까 이게 정답!
    return HttpResponseRedirect(reverse("jobTips:detail", args=[pk]))


@login_required
@require_http_methods(["GET", "POST"])
def post_create(request):
    if request.method == "POST":
        form = JobTipPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            # tags: JSON(list) or 문자열 둘 다 대응
            tags_raw = request.POST.get("tags", "")
            if tags_raw:
                try:
                    tags_list = json.loads(tags_raw)  # ["삼성", "백엔드"]
                    if isinstance(tags_list, list):
                        post.tags = ", ".join([str(t).strip() for t in tags_list if str(t).strip()])
                except json.JSONDecodeError:
                    post.tags = ", ".join([t.strip() for t in tags_raw.split(",") if t.strip()])

            post.save()
            return redirect("jobTips:detail", pk=post.pk)
    else:
        form = JobTipPostForm()

    return render(request, "jobTips/b_post.html", {
        "form": form,
        "is_edit": False,
    })


@login_required
@require_http_methods(["GET", "POST"])
def post_edit(request, pk):
    post = get_object_or_404(JobTipPost, pk=pk)

    # 본인 글만 수정 가능
    if post.author != request.user:
        return HttpResponseForbidden("수정 권한이 없습니다.")

    if request.method == "POST":
        form = JobTipPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            edited = form.save(commit=False)

            # tags: JSON(list) or 문자열 둘 다 대응
            tags_raw = request.POST.get("tags", "")
            if tags_raw:
                try:
                    tags_list = json.loads(tags_raw)
                    if isinstance(tags_list, list):
                        edited.tags = ", ".join([str(t).strip() for t in tags_list if str(t).strip()])
                except json.JSONDecodeError:
                    edited.tags = ", ".join([t.strip() for t in tags_raw.split(",") if t.strip()])

            edited.save()
            return redirect("jobTips:detail", pk=edited.pk)
    else:
        form = JobTipPostForm(instance=post)

    return render(request, "jobTips/b_post.html", {
        "form": form,
        "post": post,
        "is_edit": True,
    })


@login_required
@require_POST
def post_delete(request, pk):
    post = get_object_or_404(JobTipPost, pk=pk)

    # 본인 글만 삭제 가능
    if post.author != request.user:
        return HttpResponseForbidden("삭제 권한이 없습니다.")

    post.delete()
    return redirect("jobTips:list")


# =========================
# ✅ 댓글 (작성/삭제)
# =========================

@login_required
@require_POST
def comment_create(request, pk):
    """
    댓글 작성
    - pk: 게시글 pk (post pk)
    """
    post = get_object_or_404(JobTipPost, pk=pk)
    content = request.POST.get("content", "").strip()

    if content:
        Comment.objects.create(
            post=post,
            author=request.user,
            content=content
        )

    return redirect("jobTips:detail", pk=post.pk)


@login_required
@require_POST
def comment_delete(request, pk, comment_id):
    """
    댓글 삭제
    - pk: 게시글 pk
    - comment_id: 댓글 pk
    """
    post = get_object_or_404(JobTipPost, pk=pk)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)

    if comment.author != request.user:
        return HttpResponseForbidden("댓글 삭제 권한이 없습니다.")

    comment.delete()
    return redirect("jobTips:detail", pk=post.pk)
