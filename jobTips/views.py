import json

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.core.paginator import Paginator

from .models import JobTipPost, Comment, JobTipFile
from .forms import JobTipPostForm


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

    # ✅ 페이지네이션
    page_number = request.GET.get("page", "1")
    paginator = Paginator(posts, 8)  # 한 페이지 8개
    page_obj = paginator.get_page(page_number)

    return render(request, "jobTips/jobtips-list.html", {
        "page_obj": page_obj,
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

    is_scrapped = (
        post.scraps.filter(pk=request.user.pk).exists()
        if request.user.is_authenticated else False
    )

    tags_list = [t.strip() for t in (post.tags or "").split(",") if t.strip()]
    comments = post.comments.select_related("author").all()

    # ✅ 다중 파일: 이미지/그 외 분리
    all_files = post.files.all().order_by("created_at")
    image_files = [f for f in all_files if (f.file and str(f.file.name).lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")))]
    other_files = [f for f in all_files if f not in image_files]

    return render(request, "jobTips/jobtips-detail.html", {
        "post": post,
        "is_liked": is_liked,
        "is_scrapped": is_scrapped,
        "tags_list": tags_list,
        "comments": comments,
        "image_files": image_files,
        "other_files": other_files,
    })


@login_required
@require_POST
def post_like(request, pk):
    post = get_object_or_404(JobTipPost, pk=pk)

    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return HttpResponseRedirect(reverse("jobTips:detail", args=[pk]))


@login_required
@require_POST
def post_scrap(request, pk):
    post = get_object_or_404(JobTipPost, pk=pk)

    if post.scraps.filter(pk=request.user.pk).exists():
        post.scraps.remove(request.user)
    else:
        post.scraps.add(request.user)

    return HttpResponseRedirect(reverse("jobTips:detail", args=[pk]))


@login_required
@require_http_methods(["GET", "POST"])
def post_create(request):
    if request.method == "POST":
        form = JobTipPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            tags_raw = request.POST.get("tags", "")
            if tags_raw:
                try:
                    tags_list = json.loads(tags_raw)
                    if isinstance(tags_list, list):
                        post.tags = ", ".join([str(t).strip() for t in tags_list if str(t).strip()])
                except json.JSONDecodeError:
                    post.tags = ", ".join([t.strip() for t in tags_raw.split(",") if t.strip()])

            post.save()

            # ✅ 다중 파일 저장: name="files"
            for f in request.FILES.getlist("files"):
                JobTipFile.objects.create(post=post, file=f)

            return redirect("jobTips:detail", pk=post.pk)
    else:
        form = JobTipPostForm()

    return render(request, "jobTips/jobtips-post.html", {
        "form": form,
    })


@login_required
@require_http_methods(["GET", "POST"])
def post_edit(request, pk):
    post = get_object_or_404(JobTipPost, pk=pk)

    if post.author != request.user:
        return HttpResponseForbidden("수정 권한이 없습니다.")

    if request.method == "POST":
        form = JobTipPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            edited = form.save(commit=False)

            tags_raw = request.POST.get("tags", "")
            if tags_raw:
                try:
                    tags_list = json.loads(tags_raw)
                    if isinstance(tags_list, list):
                        edited.tags = ", ".join([str(t).strip() for t in tags_list if str(t).strip()])
                except json.JSONDecodeError:
                    edited.tags = ", ".join([t.strip() for t in tags_raw.split(",") if t.strip()])

            edited.save()

            # ✅ edit에서 새 파일 추가 (기존 파일 유지)
            for f in request.FILES.getlist("files"):
                JobTipFile.objects.create(post=edited, file=f)

            return redirect("jobTips:detail", pk=edited.pk)
    else:
        form = JobTipPostForm(instance=post)

    return render(request, "jobTips/jobtips-edit.html", {
        "form": form,
        "post": post,
    })


@login_required
@require_POST
def post_delete(request, pk):
    post = get_object_or_404(JobTipPost, pk=pk)

    if post.author != request.user:
        return HttpResponseForbidden("삭제 권한이 없습니다.")

    post.delete()
    return redirect("jobTips:list")


@login_required
@require_POST
def comment_create(request, pk):
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
    post = get_object_or_404(JobTipPost, pk=pk)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)

    if comment.author != request.user:
        return HttpResponseForbidden("댓글 삭제 권한이 없습니다.")

    comment.delete()
    return redirect("jobTips:detail", pk=post.pk)
