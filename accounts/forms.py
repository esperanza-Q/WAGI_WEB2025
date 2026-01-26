import re
from django import forms
from django.contrib.auth import get_user_model
from .models import College, Department, Verification
from .models import GradeChoices
from django.core.exceptions import ValidationError

User = get_user_model()

class SignupForm(forms.ModelForm):
    college = forms.CharField(required=True, label="단과대학")
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),
        to_field_name="dept_id",   # ⭐⭐⭐ 핵심
        required=True,
        label="학과",
    )

    username = forms.CharField(
        label="아이디(학번)",
        help_text=None,
        widget=forms.TextInput(attrs={"placeholder": "예) 20200000"}),
    )

    grade = forms.ChoiceField(
        label="학년",
        choices= GradeChoices.choices,
        required=True,
    )

    password1 = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput,
        strip=False,
        help_text="8자 이상 입력해주세요.(영문, 숫자, 특수문자 포함)",
    )

    password2 = forms.CharField(
        label="비밀번호 확인",
        widget=forms.PasswordInput,
        strip=False,
    )

    display_name = forms.CharField(max_length=100, label="닉네임")
    email = forms.EmailField(label="이메일")  

    class Meta:
        model = User
        fields = [
            "college",
            "department",
            "display_name",
            "email",
            "username",
            "grade",
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "아이디(학번)"
        self.fields["username"].help_text = None

        self.fields["department"].queryset = Department.objects.none()
        college_code = (self.data.get("college") or self.initial.get("college") or "").strip()
        if college_code and College.objects.filter(college_id=college_code).exists():
            self.fields["department"].queryset = Department.objects.filter(
                college__college_id=college_code
            ).order_by("dept_name")

    def clean_college(self):
        code = (self.cleaned_data.get("college") or "").strip()
        if not code:
            raise ValidationError("단과대를 선택해 주세요.")
        if not College.objects.filter(college_id=code).exists():
            raise ValidationError("유효하지 않은 단과대입니다.")
        return code

    def clean_username(self):
        u = self.cleaned_data["username"].strip()
        # 학번 규칙: 숫자 5~10자리 (원하면 길이 조정)
        if not re.fullmatch(r"\d{5,10}", u):
            raise ValidationError("학번은 숫자 5~10자리여야 합니다.")
        if User.objects.filter(username=u).exists():
            raise ValidationError("이미 사용 중인 학번입니다.")
        return u

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("이미 등록된 이메일입니다.")
        return email 
    
    def clean_password2(self):
        pw1 = self.cleaned_data.get("password1")
        pw2 = self.cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise ValidationError("비밀번호가 일치하지 않습니다.")
        return pw2
    
    def save(self, commit=True):
        user = super().save(commit=False)

        user.username     = self.cleaned_data["username"].strip()
        user.email = self.cleaned_data["email"].lower()
        user.display_name = (self.cleaned_data.get("display_name") or "").strip()
        user.department = self.cleaned_data["department"]
        user.grade = self.cleaned_data["grade"]

        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
        return user
    
class LoginForm(forms.Form):
    username = forms.CharField(label="아이디(학번)", max_length=150)
    password = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput,
        strip=False,
    )

class VerificationForm(forms.ModelForm):
    class Meta:
        model = Verification
        fields = ["real_name", "verification_document"]
        labels = {
            "real_name": "성명",
            "verification_document": "인증 서류",
        }
        help_texts = {
            "verification_document": "재학증명서, 학생증 등 인증용 이미지/서류(최대 10MB)",
        }
    