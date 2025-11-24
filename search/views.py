from django.http import JsonResponse
from django.db.models import Q
from django.utils.timezone import localtime

from experience.models import Review
from .utils import filter_users_by_params


def search_reviews(request):
    """
    단과대/학과/학번/검색어/카테고리/정렬 조건으로
    Review(활동 후기) 검색하는 API
    """

    # 1) 우리 학교 맞춤 필터: 단과대/학과/학번 기준으로 User 필터
    users = filter_users_by_params(request.GET)

    # 2) 추가 검색 조건 꺼내기
    q = request.GET.get("q")                    # 검색어 (제목+내용)
    category = request.GET.get("category")      # club/academic/contest/intern
    sort = request.GET.get("sort", "latest")    # latest / agree

    # 3) 조건에 맞는 유저들이 쓴 후기만 가져오기
    reviews = Review.objects.filter(user__in=users)

    # 4) 카테고리 필터 (동아리/학회/공모전/인턴)
    if category:
        reviews = reviews.filter(category=category)

    # 5) 검색어 필터 (제목 + 내용)
    if q:
        reviews = reviews.filter(
            Q(title__icontains=q) |
            Q(content__icontains=q)
        )

    # 6) 정렬 옵션
    if sort == "agree":
        # 공감순 정렬 (like_count는 property라 파이썬에서 정렬)
        reviews = sorted(reviews, key=lambda r: r.like_count, reverse=True)
    else:
        # 기본: 최신순
        reviews = reviews.order_by("-created_at")

    # 7) JSON 응답 데이터 만들기
    results = []
    for review in reviews:
        user = review.user
        dept = user.department
        college = dept.college if dept else None

        created = localtime(review.created_at).strftime("%Y-%m-%d")

        results.append({
            "board": "review",                # 어떤 게시판인지 표시
            "id": review.id,
            "title": review.title,
            "content_preview": review.content[:100],  # 앞 100자만
            "rating": review.rating,
            "category": review.get_category_display(),  # "동아리" 같은 한글
            "created_at": created,
            "like_count": review.like_count,
            "author": {
                "id": user.id,
                "username": user.username,          # 학번
                "display_name": user.display_name,  # 이름/닉네임
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
        json_dumps_params={"ensure_ascii": False},  # 한글 깨짐 방지
    )