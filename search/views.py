#활동후기게시판
from django.shortcuts import render
from experience.models import Review
from django.db.models import Q
import re


# --- 검색 테스트용 뷰 (search/expr/) ---
def search_expr_test(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    order = request.GET.get('order', 'latest')
    college = request.GET.get('college', '')
    department = request.GET.get('department', '')
    grade = request.GET.get('grade', '')

    # Step 1: 카테고리 필터 (항상 가장 먼저 적용)
    reviews = Review.objects.all()
    if category:
        reviews = reviews.filter(category=category)

    # Step 2: 맞춤필터링 (카테고리 내에서 적용)
    if college:
        reviews = reviews.filter(user__department__college__college_name=college)
    if department:
        reviews = reviews.filter(user__department__dept_name=department)
    if grade:
        reviews = reviews.filter(user__username__startswith=grade)

    # Step 3: 텍스트 검색 (카테고리+맞춤필터링 내에서 적용)
    if query and query.strip():
        keywords = [w.strip() for w in re.split(r'[ ,]+', query) if w.strip()]
        q_obj = Q()
        for word in keywords:
            regex = r'(^|\s)' + re.escape(word) + r'($|\s)'
            q_obj |= Q(title__regex=regex) | Q(content__regex=regex)
        reviews = reviews.filter(q_obj).distinct()

    # Step 4: 정렬 (카테고리+맞춤필터+검색 내에서 적용)
    if order == 'rating':
        reviews = reviews.order_by('-rating')
    elif order == 'agree':
        # like_count는 DB 필드가 아니므로 파이썬 정렬 사용
        reviews = sorted(reviews, key=lambda r: getattr(r, 'like_count', 0), reverse=True)
    else:  # 'latest' or default
        reviews = reviews.order_by('-created_at')
            

    # 드롭다운용 목록 준비
    from accounts.models import College, Department, User
    college_list = list(College.objects.values_list('college_name', flat=True))
    department_list = list(Department.objects.values_list('dept_name', flat=True))
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
    return render(request, "experience-list.html", context)

# --- 검색 테스트용 HTML 뷰 복구 (search/reviews/test/) ---
def search_reviews_page(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '전체')
    order = request.GET.get('order', 'latest')
    status = request.GET.get('status', '')
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
        'order': order,  # 항상 order 포함
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
def search_recruit(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    order = request.GET.get('order', 'latest')
    college = request.GET.get('college', '')
    department = request.GET.get('department', '')
    grade = request.GET.get('grade', '')
    status = request.GET.get('status', '')



    posts = Recruit.objects.all()
    # 1. 카테고리 필터
    if category:
        posts = posts.filter(category__category_name=category)

    # 2. 모집중/모집완료(상태) 필터
    if status == 'open':
        posts = posts.filter(is_recruiting=True)
    elif status == 'closed':
        posts = posts.filter(is_recruiting=False)

    # 3. 맞춤 필터링 (단과대, 학과, 학년)
    if college:
        posts = posts.filter(college__college_name=college)
    if department:
        posts = posts.filter(user__department__dept_name=department)
    if grade:
        posts = posts.filter(user__username__startswith=grade)

    # 4. 텍스트 검색 (활동명 등)
    if query and query.strip():
        keywords = [w.strip() for w in re.split(r'[ ,]+', query) if w.strip()]
        q_obj = Q()
        for word in keywords:
            regex = r'(^|\s)' + re.escape(word) + r'($|\s)'
            q_obj |= Q(title__regex=regex) | Q(body__regex=regex)
        posts = posts.filter(q_obj).distinct()

    # 5. 정렬
    if order == 'latest':
        posts = posts.order_by('-created_at')
    elif order == 'rating':
        posts = posts.order_by('-rating') if hasattr(Recruit, 'rating') else posts
    elif order == 'agree':
        posts = sorted(posts, key=lambda p: getattr(p, 'like_count', 0), reverse=True)

    college_list = list(College.objects.values_list('college_name', flat=True))
    department_list = list(Department.objects.values_list('dept_name', flat=True))
    grade_list = sorted(set([u[:4] for u in User.objects.values_list('username', flat=True) if len(u) >= 4]))

    context = {
        'recruits': posts,
        'q_query': query,
        'category': category,
        'categories': ['전체', '동아리', '공모전', '스터디'],
        'order': order,
        'status': status,  # 상태 필터 값도 context에 추가
        'selected_college': college,
        'selected_department': department,
        'selected_grade': grade,
        'college_list': college_list,
        'department_list': department_list,
        'grade_list': grade_list,
    }
    return render(request, "recruit-list.html", context)

# --- 취업후기게시판(커리어) 검색/필터/정렬 뷰 ---
def search_jobTips(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    order = request.GET.get('order', 'latest')
    college = request.GET.get('college', '')
    department = request.GET.get('department', '')
    grade = request.GET.get('grade', '')

    from career.models import CareerReview
    reviews = CareerReview.objects.all()
    if category:
        reviews = reviews.filter(category=category)
    if college:
        reviews = reviews.filter(user__department__college__college_name=college)
    if department:
        reviews = reviews.filter(user__department__dept_name=department)
    if grade:
        reviews = reviews.filter(user__username__startswith=grade)
    if query and query.strip():
        keywords = [w.strip() for w in re.split(r'[ ,]+', query) if w.strip()]
        q_obj = Q()
        for word in keywords:
            regex = r'(^|\s)' + re.escape(word) + r'($|\s)'
            q_obj |= Q(title__regex=regex) | Q(content__regex=regex)
        reviews = reviews.filter(q_obj).distinct()
    if order == 'rating':
        reviews = reviews.order_by('-rating') if hasattr(CareerReview, 'rating') else reviews
    elif order == 'agree':
        reviews = sorted(reviews, key=lambda r: getattr(r, 'like_count', 0), reverse=True)
    else:
        reviews = reviews.order_by('-created_at')

    from accounts.models import College, Department, User
    college_list = list(College.objects.values_list('college_name', flat=True))
    department_list = list(Department.objects.values_list('dept_name', flat=True))
    grade_list = sorted(set([u[:4] for u in User.objects.values_list('username', flat=True) if len(u) >= 4]))

    context = {
        'reviews': reviews,
        'q_query': query,
        'category': category,
        'categories': ['전체', '자소서', '면접', '포트폴리오'],
        'order': order,
        'selected_college': college,
        'selected_department': department,
        'selected_grade': grade,
        'college_list': college_list,
        'department_list': department_list,
        'grade_list': grade_list,
    }
    return render(request, "jobTips-list.html", context)
