from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

def verification_doc_upload_path(instance, filename): #파일 저장 경로를 사용자별 폴더 구조로 자동 분류
    pk = instance.pk or "pending"
    return f"verification_docs/{pk}/{filename}"

def validate_file_size(file): #파일 크기 검증 함수
    max_bytes = 10 * 1024 * 1024  # 10MB
    if file and file.size > max_bytes:
        raise ValidationError("파일 크기는 10MB 이하여야 합니다.")

# Create your models here.
#단과대명
class College(models.Model):
    college_name = models.CharField(max_length=100, unique=True)
    college_id = models.CharField(max_length=10, unique=True)
    
    class Meta:
        verbose_name = "단과대학" #관리자 페이지에서 보여질 이름
        verbose_name_plural = "단과대학 목록"
        ordering = ["college_name"] #단과대 이름 순으로 정렬하기

    def __str__(self):
        return self.college_name

#학과명
class Department(models.Model):
    dept_name = models.CharField(max_length=100)
    dept_id = models.CharField(max_length=10, unique=True)
    college = models.ForeignKey(
        College, 
        on_delete=models.PROTECT,
        related_name="departments",
    )

    class Meta:
        verbose_name = "학과"
        verbose_name_plural = "학과 목록"
        ordering = ["college__college_name", "dept_name"] #단과대 이름, 학과 이름 순으로 정렬하기
        constraints = [
            models.UniqueConstraint(
                fields=["college", "dept_name"],
                name="uniq_dept_name_in_same_college",
            )
        ]
        indexes = [
            models.Index(fields=["college", "dept_name"]),
            models.Index(fields=["dept_id"]),
        ]

    def __str__(self):
         return f"{self.college.college_name} / {self.dept_name}"

#유저
class User(AbstractUser): #기본적으로 username, password, email, is_active 등 이미 포함되어 있음
    #user_id = models.CharField(max_length=50, unique=True) #username이랑 중복된다고 생각해서 제거
    display_name = models.CharField(max_length=100) #닉네임(중복 허용)
    student_id = models.CharField(max_length=20, unique=True) #학번
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False) #학교 인증 여부
    verification_document = models.FileField( #학교 인증용 서류
        upload_to=verification_doc_upload_path,
        null=True,
        blank=True, 
        validators = [
            FileExtensionValidator(["pdf"]), 
            validate_file_size,
        ],
        help_text="재학증명서 등 학교 인증용 서류(PDF, 최대 10MB)를 업로드하세요."
    ) 
    verified_at = models.DateTimeField(null=True, blank=True) #관리자가 승인한 날짜/시간 저장
    verified_by = models.ForeignKey( #이 사용자를 인증한 관리자(User)를 가리키는 외래키
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="verified_users",
        help_text="이 사용자를 인증한 관리자",
        limit_choices_to={"is_staff": True},
    )
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, #학과가 삭제되더라도 유저 정보는 유지
        null=True, 
        related_name="users",
    )

    class Meta:
        verbose_name = "유저"
        verbose_name_plural = "유저 목록"
        ordering = ["-date_joined", "id"] #가입날 최신순으로, id는 오름차순
        indexes = [
            models.Index(fields=["student_id"]),
            models.Index(fields=["email"]),
            models.Index(fields=["department"]),
            models.Index(fields=["is_verified"]),
        ]
        
    def __str__(self):
        return self.student_id #학번(student_id)으로 구분


