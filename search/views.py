from django.shortcuts import render
from experience.models import Review
from django.db.models import Q
import re

# --- 검색 테스트용 뷰 (search/expr/) ---
def search_expr_test(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '전체')
    sort = request.GET.get('sort', 'latest')
    category_map = {
        '동아리': 'club',
        '학회': 'academic',
        '공모전': 'contest',
        '인턴': 'intern',
    }
    code = category_map.get(category, None) if category != '전체' else None

    # 카테고리 필터
    if code:
        reviews = Review.objects.filter(category=code)
    else:
        reviews = Review.objects.all()

    # 검색어 필터
    if query and query.strip():
        words = [w.strip() for w in re.split(r'[ ,]+', query) if w.strip()]
        q_obj = Q()
        for word in words:
            if word.startswith('#'):
                q_obj |= Q(tags__name__icontains=word[1:])
            else:
                q_obj |= (Q(title__icontains=word) | Q(content__icontains=word))
        reviews = reviews.filter(q_obj).distinct()
        def count_score(review):
            score = 0
            for w in words:
                if w.startswith('#'):
                    score += sum([1 for tag in getattr(review, 'tags', []).all() if w[1:] in tag.name])
                else:
                    score += review.title.count(w)
                    score += review.content.count(w)
            return score
        reviews = sorted(reviews, key=count_score, reverse=True)
    else:
        if sort == 'agree':
            reviews = sorted(reviews, key=lambda r: r.like_count, reverse=True)
        else:
            reviews = reviews.order_by('-created_at')

    context = {
        'reviews': reviews,
        'q_query': query,
        'category': category,
        'categories': ['전체', '동아리', '학회', '공모전', '인턴'],
        'sort': sort,
    }
    return render(request, "b_search_expr.html", context)
from django.http import JsonResponse
from django.db.models import Q
from django.utils.timezone import localtime
from django.shortcuts import render  

from experience.models import Review
from .utils import filter_users_by_params


def search_reviews(request):
    """
    JSON API: /search/reviews/
    """
    users = filter_users_by_params(request.GET)

    q = request.GET.get("q")
    category = request.GET.get("category")
    sort = request.GET.get("sort", "latest")

    reviews = Review.objects.filter(user__in=users)

    if category:
        reviews = reviews.filter(category=category)

    if q:
        reviews = reviews.filter(
            Q(title__icontains=q) |
            Q(content__icontains=q)
        )

    if sort == "agree":
        reviews = sorted(reviews, key=lambda r: r.like_count, reverse=True)
    else:
        reviews = reviews.order_by("-created_at")

    results = []
    for review in reviews:
        user = review.user
        dept = user.department
        college = dept.college if dept else None

        created = localtime(review.created_at).strftime("%Y-%m-%d")

        results.append({
            "board": "review",
            "id": review.id,
            "title": review.title,
            "content_preview": review.content[:100],
            "rating": review.rating,
            "category": review.get_category_display(),
            "created_at": created,
            "like_count": review.like_count,
            "author": {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "grade": user.grade,
                "is_verified": user.is_verified,
                "department": dept.dept_name if dept else None,
                "department_id": dept.dept_id if dept else None,
                "college": college.college_name if college else None,
                "college_id": college.college_id if college else None,
            }
        })

    return JsonResponse(
        {"results": results, "count": len(results)},
        status=200,
        json_dumps_params={"ensure_ascii": False},
    )


# 👇 새로 추가된 HTML 테스트용 뷰
def search_reviews_page(request):
    """
    HTML 테스트용: /search/reviews/test/
    """
    users = filter_users_by_params(request.GET)

    q = request.GET.get("q")
    category = request.GET.get("category")
    sort = request.GET.get("sort", "latest")

    reviews = Review.objects.filter(user__in=users)

    # 검색어가 입력되지 않으면 해당 user들이 쓴 모든 글을 보여줌
    if q and q.strip():
        import re
        words = [w.strip() for w in re.split(r'[ ,]+', q) if w.strip()]
        q_obj = Q()
        for word in words:
            if word.startswith('#'):
                q_obj |= Q(tags__name__icontains=word[1:])
            else:
                q_obj |= (Q(title__icontains=word) | Q(content__icontains=word))
        reviews = reviews.filter(q_obj)

    if category:
        reviews = reviews.filter(category=category)

    if isinstance(reviews, list):
        # 검색어 없을 때 빈 리스트
        pass
    elif sort == "agree":
        reviews = sorted(reviews, key=lambda r: r.like_count, reverse=True)
    else:
        reviews = reviews.order_by("-created_at")

    context = {
        "reviews": reviews,
        "params": request.GET,
    }
    return render(request, "search_test.html", context)
