from django.shortcuts import render, redirect
from .forms import SignupForm, LoginForm, VerificationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from .models import Department, Verification
from django.contrib.auth.decorators import login_required

# Create your views here.
#회원가입 뷰
def signup_view(request):
    college_id = request.GET.get("college") if request.method == "GET" else request.POST.get("college")

    if request.method == "GET":
        form = SignupForm(
            college_id=college_id,  # ← forms.py의 __init__(..., college_id=...) 받도록 되어 있어야 함
            initial={"college": college_id} if college_id else None
        )
        return render(request, "b_signup.html", {"form": form})

    # POST (최종 제출)
    form = SignupForm(request.POST, request.FILES, college_id=college_id)
    if form.is_valid():
        form.save(commit=True)
        messages.success(request, "회원가입이 완료되었습니다. 로그인해주세요.")
        return redirect("accounts:login")

    messages.error(request, "회원가입에 실패했습니다. 다시 시도해주세요.")
    return render(request, "b_signup.html", {"form": form})

#로그인 뷰
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "로그인 성공!")
                return redirect("accounts:verification")
            else:
                messages.error(request, "아이디 또는 비밀번호가 올바르지 않습니다.")
        else:
            messages.error(request, "로그인에 실패했습니다. 다시 시도해주세요.")

        return render(request, "b_login.html", {"form": form})
    else:
        form = LoginForm()
        return render(request, "b_login.html", {"form": form})

#로그아웃 뷰
def logout_view(request):
    logout(request)
    messages.info(request, "로그아웃되었습니다.")
    return redirect("home")

def departments_api(request):
    college_id = request.GET.get("college") or request.GET.get("college_id")
    if not college_id:
        return JsonResponse({"departments": []})
    qs = Department.objects.filter(
        college__id=college_id  
    ).order_by("dept_name").values("id", "dept_name")
    return JsonResponse({"departments": list(qs)})

@login_required
def verification_view(request):
    # 이미 인증 요청한 기록이 있는지 확인 (OneToOne 이라 하나만 존재)
    try:
        verification_obj = request.user.verification
    except Verification.DoesNotExist:
        verification_obj = None

    if request.method == "POST":
        # 기존 것이 있으면 수정, 없으면 새로 생성
        form = VerificationForm(
            request.POST,
            request.FILES,
            instance=verification_obj,
        )
        if form.is_valid():
            ver = form.save(commit=False)
            ver.user = request.user           # 외래키 연결
            ver.is_verified = False           # 새로 올리면 항상 미승인 상태로
            ver.save()

            messages.success(
                request,
                "인증 요청이 제출되었습니다. 관리자의 승인을 기다려주세요.",
            )
            return redirect("home")  # 프로젝트 메인 url 이름에 맞게 수정
    else:
        form = VerificationForm(instance=verification_obj)

    context = {
    "form": form,
    "user_obj": request.user,
    "verification_obj": verification_obj,
    }
    return render(request, "b_verification.html", context)