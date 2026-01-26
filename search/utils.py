from django.contrib.auth import get_user_model

User = get_user_model()

def filter_users_by_params(params):
    """
    단과대/학과/학번(year) 조건으로 User를 필터링하는 공통 함수.
    params: request.GET 처럼 딕셔너리 비슷한 객체
    """
    college_id = params.get("college_id")  # ex) 'C01'
    dept_id = params.get("dept_id")        # ex) 'D01'
    year = params.get("year")              # ex) '21' (학번 앞 2자리)

    # department, college까지 한 번에 가져오도록 select_related
    qs = User.objects.select_related(
        "department",
        "department__college",
    ).all()

    if college_id:
        qs = qs.filter(department__college__college_id=college_id)

    if dept_id:
        qs = qs.filter(department__dept_id=dept_id)

    if year:
        # username = 학번 이니까, '21'로 시작하는 학번 필터
        qs = qs.filter(username__startswith=year)

    return qs