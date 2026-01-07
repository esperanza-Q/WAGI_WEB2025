from django.shortcuts import render, redirect, get_object_or_404
from .models import Review, ReviewLike, ActivityCategory, ReviewScrap, ReviewFile, Tag
from .forms import ReviewForm, ReviewFileMultipleForm
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from .models import ReviewComment

def review_list(request):
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    tag_name = request.GET.get('tag', '')
    query = request.GET.get('q')
    college = request.GET.get('college', '')  # 단과대
    department = request.GET.get('department', '')  # 학과
    grade = request.GET.get('grade', '')  # 학년(학번)

    reviews = Review.objects.all().annotate(
        like_count_db=Count('reviewlike', filter=Q(reviewlike__is_agree=True))
    )

    # 카테고리 필터
    if category:
        reviews = reviews.filter(category=category)
    # 검색 기능
    if search:
        reviews = reviews.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search)
        )
    if tag_name:
        reviews = reviews.filter(tags__name=tag_name)
    if query:
        reviews = reviews.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )

    # 맞춤 필터링: 단과대, 학과, 학년(grade)
    if college:
        reviews = reviews.filter(user__department__college__college_name=college)
    if department:
        reviews = reviews.filter(user__department__dept_name=department)
    if grade:
        reviews = reviews.filter(user__grade=grade)

    context = {
        'reviews': reviews.distinct(),
        'selected_category': category,
        'search_query': search,
        'selected_tag': tag_name,
        'categories': ActivityCategory.choices,
        'selected_college': college,
        'selected_department': department,
        'selected_grade': grade,
    }

    return render(request, "experience-list.html", context)

def review_create(request):
    file_form = ReviewFileMultipleForm()
    if request.method == "POST":
        form = ReviewForm(request.POST)
        file_form = ReviewFileMultipleForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            tag_string = request.POST.get("tags", "")
            tag_names = [t.strip() for t in tag_string.split(",") if t.strip()]
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                review.tags.add(tag)
            for f in request.FILES.getlist("files"):
                ReviewFile.objects.create(review=review, file=f)
            return redirect("experience:review_list")
    else:
        form = ReviewForm()
    return render(request, "experience-post.html", {
        "form": form,
        "file_form": file_form
    })

def review_detail(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    comments = review.comments.all().order_by("-created_at")
    files = review.files.all()
    like_count = ReviewLike.objects.filter(review=review, is_agree=True).count()
    user_like = None
    if request.user.is_authenticated:
        user_like = ReviewLike.objects.filter(review=review, user=request.user).first()
    scrapped_by_user = False
    if request.user.is_authenticated:
        scrapped_by_user = review.scraps.filter(user=request.user).exists()
    context = {
        "review": review,
        "comments": comments,
        "files": files,
        "like_count": like_count,
        "scrapped_by_user": scrapped_by_user,
        "user_like": user_like,
    }
    return render(request, "experience-detail.html", context)

@login_required
def toggle_like(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    like, created = ReviewLike.objects.get_or_create(review=review, user=request.user)

    # 이미 좋아요 → 취소
    if not created and like.is_agree:
        like.delete()
    else:
        like.is_agree = True
        like.save()

    return redirect("experience:review_detail", review_id=review_id)

@login_required
def add_comment(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    content = request.POST.get("content")

    if content:
        ReviewComment.objects.create(
            review=review,
            user=request.user,
            content=content
        )

    return redirect("experience:review_detail", review_id=review_id)

@login_required
def delete_comment(request, review_id, comment_id):
    comment = get_object_or_404(ReviewComment, id=comment_id, review_id=review_id)

    # 작성자 본인만 삭제 가능
    if comment.user != request.user:
        return redirect("experience:review_detail", review_id=review_id)

    comment.delete()
    return redirect("experience:review_detail", review_id=review_id)

@login_required
def review_edit(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # 작성자만 수정 가능
    if review.user != request.user:
        return redirect("experience:review_detail", review_id=review.id)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        file_form = ReviewFileMultipleForm(request.POST, request.FILES)

        print("FILES 개수:", len(request.FILES.getlist("files")))
        print("FILES 목록:", request.FILES.getlist("files"))

        if form.is_valid():
            form.save()
            review.tags.clear()
            #새 태그 저장
            tag_string = form.cleaned_data.get("tags", "")
            tag_names = [t.strip() for t in tag_string.split(",") if t.strip()]
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                review.tags.add(tag)
            #새 첨부파일 추가
            for f in request.FILES.getlist('files'):
                ReviewFile.objects.create(review=review, file=f)

            return redirect("experience:review_detail", review_id=review.id)
        else:
            print("❌ 수정 폼 에러:", form.errors)
    else:
        form = ReviewForm(
            instance=review,
            initial={
                "tags": ", ".join(review.tags.values_list("name", flat=True))
            })
        file_form = ReviewFileMultipleForm()

    return render(request, "experience-edit.html", {
        "form": form,
        "file_form": file_form,
        "review": review,
        "files": review.files.all(),
    })

@login_required
def delete_file(request, file_id):
    file = get_object_or_404(ReviewFile, id=file_id)

    if file.review.user != request.user:
        return redirect("experience:review_detail", review_id=file.review.id)

    review_id = file.review.id
    file.delete()

    return redirect("experience:review_edit", review_id=review_id)

@login_required
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # 작성자 본인만 삭제 가능
    if review.user != request.user:
        return redirect("experience:review_detail", review_id=review.id)

    review.delete()
    return redirect("experience:review_list")

@login_required
def toggle_scrap(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    scrap, created = ReviewScrap.objects.get_or_create(
        review=review,
        user=request.user,
    )

    if not created:
        # 이미 스크랩 되어있으면 → 삭제(언스크랩)
        scrap.delete()

    return redirect("experience:review_detail", review_id=review.id)
