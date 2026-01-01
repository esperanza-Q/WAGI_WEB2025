from django.shortcuts import render, redirect, get_object_or_404
from .models import Review, ReviewLike, ActivityCategory, ReviewScrap, ReviewFile
from .forms import ReviewForm, ReviewImageMultipleForm, ReviewFileMultipleForm
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from .models import ReviewComment, ReviewImage

def review_list(request):
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
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
        'reviews': reviews,
        'selected_category': category,
        'search_query': search,
        'categories': ActivityCategory.choices,
        'selected_college': college,
        'selected_department': department,
        'selected_grade': grade,
    }

    return render(request, "b_review_list.html", context)

def review_create(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        image_form = ReviewImageMultipleForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            images = request.FILES.getlist('images')
            for img in images:
                ReviewImage.objects.create(review=review, image=img)
            files = request.FILES.getlist("files")
            for f in files:
                ReviewFile.objects.create(review=review, file=f)
            return redirect("review_list")
    else:
        form = ReviewForm()
        image_form = ReviewImageMultipleForm()
        file_form = ReviewFileMultipleForm()
    return render(request, "b_review_create.html", {
        "form": form,
        "image_form": image_form,
        "file_form": file_form
    })

def review_detail(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    images = review.images.all()
    comments = review.comments.all().order_by("-created_at")
    like_count = ReviewLike.objects.filter(review=review, is_agree=True).count()
    user_like = None
    if request.user.is_authenticated:
        user_like = ReviewLike.objects.filter(review=review, user=request.user).first()
    scrapped_by_user = False
    if request.user.is_authenticated:
        scrapped_by_user = review.scraps.filter(user=request.user).exists()
    context = {
        "review": review,
        "images": images,
        "comments": comments,
        "like_count": like_count,
        "scrapped_by_user": scrapped_by_user,
        "user_like": user_like,
    }
    return render(request, "b_review_detail.html", context)

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

    return redirect("review_detail", review_id=review_id)

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

    return redirect("review_detail", review_id=review_id)

@login_required
def delete_comment(request, review_id, comment_id):
    comment = get_object_or_404(ReviewComment, id=comment_id, review_id=review_id)

    # 작성자 본인만 삭제 가능
    if comment.user != request.user:
        return redirect("review_detail", review_id=review_id)

    comment.delete()
    return redirect("review_detail", review_id=review_id)

@login_required
def review_edit(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # 작성자만 수정 가능
    if review.user != request.user:
        return redirect("review_detail", review_id=review.id)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        image_form = ReviewImageMultipleForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            # 새 이미지 추가
            new_images = request.FILES.getlist('images')
            for img in new_images:
                ReviewImage.objects.create(review=review, image=img)

            return redirect("review_detail", review_id=review.id)

    else:
        form = ReviewForm(instance=review)
        image_form = ReviewImageMultipleForm()

    return render(request, "b_review_edit.html", {
        "form": form,
        "image_form": image_form,
        "review": review
    })

@login_required
def delete_image(request, image_id):
    image = get_object_or_404(ReviewImage, id=image_id)
    
    # 작성자 본인만 삭제 가능
    if image.review.user != request.user:
        return redirect("review_detail", review_id=image.review.id)

    review_id = image.review.id
    image.delete()

    return redirect("review_edit", review_id=review_id)

@login_required
def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # 작성자 본인만 삭제 가능
    if review.user != request.user:
        return redirect("review_detail", review_id=review.id)

    review.delete()
    return redirect("review_list")

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

    return redirect("review_detail", review_id=review.id)
