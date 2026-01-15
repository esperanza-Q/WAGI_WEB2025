
#활동후기게시판
from django.shortcuts import render
from experience.models import Review
from django.db.models import Q
import re


# --- 검색 테스트용 뷰 (search/expr/) ---
def search_expr_test(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '전체')
    order = request.GET.get('order', 'latest')
    college = request.GET.get('college', '')
    department = request.GET.get('department', '')
    grade = request.GET.get('grade', '')
    

    # 카테고리 필터
    if category and category != '전체':
        reviews = Review.objects.filter(category=category)
    else:
        reviews = Review.objects.all()

    # 맞춤필터링: 단과대, 학과, 학번
    if college:
        reviews = reviews.filter(user__department__college__college_name=college)
    if department:
        reviews = reviews.filter(user__department__dept_name=department)
    if grade:
        reviews = reviews.filter(user__username__startswith=grade)

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
        if order == 'agree':
            reviews = sorted(reviews, key=lambda r: r.like_count, reverse=True)
        elif order == 'rating':
            reviews = reviews.order_by('-rating')
        else:  # 최신순
            reviews = reviews.order_by('-created_at')
            

    # 드롭다운용 목록 준비
    from accounts.models import College, Department, User
    college_list = list(College.objects.values_list('college_name', flat=True))
    department_list = list(Department.objects.values_list('dept_name', flat=True))
    print("[DEBUG] department_list:", department_list)
    grade_list = sorted(set([u[:4] for u in User.objects.values_list('username', flat=True) if len(u) >= 4]))

    context = {
        'reviews': reviews,
        'q_query': query,
        'category': category,
        'categories': ['전체', '동아리', '학회', '공모전', '인턴'],
        'order': order,
        'selected_college': college,
        'selected_department': department,
        'selected_grade': grade,
        'college_list': college_list,
        'department_list': department_list,
        'grade_list': grade_list,
    }
    return render(request, "b_search_expr.html", context)

# --- 검색 테스트용 HTML 뷰 복구 (search/reviews/test/) ---
def search_reviews_page(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '전체')
    order = request.GET.get('order', 'latest')
    category_map = {
        '동아리': 'club',
        '학회': 'academic',
        '공모전': 'contest',
        '인턴': 'intern',
    }
    code = category_map.get(category, None) if category != '전체' else None
    if code:
        reviews = Review.objects.filter(category=code)
    else:
        reviews = Review.objects.all()
    if query and query.strip():
        words = [w.strip() for w in re.split(r'[ ,]+', query) if w.strip()]
        q_obj = Q()
        for word in words:
            if word.startswith('#'):
                q_obj |= Q(tags__name__icontains=word[1:])
            else:
                q_obj |= (Q(title__icontains=word) | Q(content__icontains=word))
        reviews = reviews.filter(q_obj).distinct()
    if order == 'agree':
        reviews = sorted(reviews, key=lambda r: r.like_count, reverse=True)
    else:
        reviews = reviews.order_by('-created_at')
    context = {
        'reviews': reviews,
        'q_query': query,
        'category': category,
        'categories': ['전체', '동아리', '학회', '공모전', '인턴'],
        'order': order,
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
 # 모집게시판
from recruit.models import Recruit
from accounts.models import College, Department, User
from django.db.models import Q
import re
 # --- 검색 테스트용 뷰 (search/recruit/) ---
def search_recruit_posts(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '전체')
    college = request.GET.get('college', '')
    department = request.GET.get('department', '')
    grade = request.GET.get('grade', '')

    category_map = {
        '동아리': 'club',
        '공모전': 'contest',
        '스터디': 'study',
    }
    code = category_map.get(category, None) if category != '전체' else None

    # 카테고리 필터
    if code:
        posts = Recruit.objects.filter(category__category_name=category)
    else:
        posts = Recruit.objects.all()

    # 맞춤필터링: 단과대, 학과, 학번
    if college:
        posts = posts.filter(college__college_name=college)
    if department:
        posts = posts.filter(user__department__dept_name=department)
    if grade:
        posts = posts.filter(user__username__startswith=grade)

    # 검색어 필터 (제목+본문)
    if query and query.strip():
        words = [w.strip() for w in re.split(r'[ ,]+', query) if w.strip()]
        q_obj = Q()
        for word in words:
            q_obj |= Q(title__icontains=word) | Q(body__icontains=word)
        posts = posts.filter(q_obj).distinct()

    # 드롭다운용 목록 준비
    college_list = list(College.objects.values_list('college_name', flat=True))
    department_list = list(Department.objects.values_list('dept_name', flat=True))
    grade_list = sorted(set([u[:4] for u in User.objects.values_list('username', flat=True) if len(u) >= 4]))

    context = {
        'posts': posts,
        'q_query': query,
        'category': category,
        'categories': ['전체', '동아리', '공모전', '스터디'],
        'order': order,
        'selected_college': college,
        'selected_department': department,
        'selected_grade': grade,
        'college_list': college_list,
        'department_list': department_list,
        'grade_list': grade_list,
    }
    return render(request, "b_search_recruit.html", context)
from accounts.models import College, Department, User
from django.db.models import Q
import re
# --- 검색 테스트용 뷰 (search/career/) ---
def search_career_reviews(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '전체')
    order = request.GET.get('order', 'latest')
# from django.db.models import Q
# import re
# # --- 검색 테스트용 뷰 (search/recruit/) ---
# def search_recruit_posts(request):
#     query = request.GET.get('q', '')
#     category = request.GET.get('category', '전체')
#     college = request.GET.get('college', '')
#     department = request.GET.get('department', '')
#     grade = request.GET.get('grade', '')

#     category_map = {
#         '동아리': 'club',
#         '공모전': 'contest',
#         '스터디': 'study',
#     }
#     code = category_map.get(category, None) if category != '전체' else None

#     # 카테고리 필터
#     if code:
#         posts = RecruitPost.objects.filter(category=code)
#     else:
#         posts = RecruitPost.objects.all()

#     # 맞춤필터링
#     if college:
#         posts = posts.filter(user__department__college__college_name=college)
#     if department:
#         posts = posts.filter(user__department__dept_name=department)
#     if grade:
#         posts = posts.filter(user__student_id__startswith=grade)

#     # 검색어 필터
#     if query and query.strip():
#         words = [w.strip() for w in re.split(r'[ ,]+', query) if w.strip()]
#         q_obj = Q()
#         for word in words:
#             q_obj |= Q(title__icontains=word) | Q(content__icontains=word)
#         posts = posts.filter(q_obj).distinct()

#     # 드롭다운용 목록 준비
#     college_list = list(College.objects.values_list('college_name', flat=True))
#     department_list = list(Department.objects.values_list('dept_name', flat=True))
#     grade_list = sorted(set([u[:4] for u in User.objects.values_list('student_id', flat=True) if len(u) >= 4]))

#     context = {
#         'posts': posts,
#         'q_query': query,
#         'category': category,
#         'categories': ['전체', '동아리', '공모전', '스터디'],
#         'selected_college': college,
#         'selected_department': department,
#         'selected_grade': grade,
#         'college_list': college_list,
#         'department_list': department_list,
#         'grade_list': grade_list,
#     }
#     return render(request, "b_search_recruit.html", context)