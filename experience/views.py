from django.shortcuts import render, redirect, get_object_or_404
from .models import Review, ReviewLike, ActivityCategory
from .forms import ReviewForm, ReviewImageMultipleForm
from .models import ReviewImage
from django.db.models import Count, Q

def review_list(request):
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    query = request.GET.get('q')

    reviews = Review.objects.all().annotate(
        like_count=Count('reviewlike', filter=Q(reviewlike__is_agree=True))
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
    context = {
        'reviews': reviews,
        'selected_category': category,
        'search_query': search,
        'categories': ActivityCategory.choices,
    }

    return render(request, "b_review_list.html", {"reviews": reviews}, context)

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
            return redirect("review_list")
    else:
        form = ReviewForm()
        image_form = ReviewImageMultipleForm()
    return render(request, "b_review_create.html", {
        "form": form,
        "image_form": image_form
    })

from .models import ReviewLike

def review_like(request, review_id, value):
    review = get_object_or_404(Review, id=review_id)

    like, created = ReviewLike.objects.get_or_create(
        review=review,
        user=request.user,
        defaults={'is_agree': value}
    )

    if not created:
        like.is_agree = value
        like.save()

    return redirect("review_detail", review_id=review.id)

def review_detail(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    return render(request, 'b_review_detail.html', {'review': review})