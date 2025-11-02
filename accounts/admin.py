from django.contrib import admin
from django.utils import timezone
from .models import User, College, Department

# Register your models here.
#단과대
@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ("college_name", "college_id")
    search_fields = ("college_name", "college_id")
    ordering = ("college_name",)

#학과
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("dept_name", "dept_id", "college")
    search_fields = ("dept_name", "dept_id", "college__college_name")
    list_filter = ("college",)
    ordering = ("college__college_name", "dept_name")

#유저
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "display_name", "student_id", "email", "is_verified", "verified_at", "department", "college")
    search_fields = ("username", "display_name", "student_id", "email", "department__dept_name", "department__college__college_name")
    list_filter = ("is_verified", "department", "department__college")
    readonly_fields = ("verified_at",)
    actions = ["approve_users", "unapprove_users"]
    ordering = ("-date_joined",)
    list_select_related = ("department", "department__college")

    # 유저에 단과대 정보 추가
    @admin.display(description="단과대학", ordering="department__college__college_name")
    def college(self, obj):
        return obj.department.college.college_name if obj.department and obj.department.college else "-"

    # approve_users: 선택한 사용자들의 is_verified를 True로 설정하고 verified_at에 현재 시간 저장
    @admin.action(description="선택 사용자 인증 승인 처리")
    def approve_users(self, request, queryset):
        updated = queryset.update(is_verified=True, verified_at=timezone.now())
        self.message_user(request, f"{updated}명의 사용자를 승인했습니다.")

    # unapprove_users: 선택한 사용자들의 is_verified를 False로 설정하고 verified_at을 None으로 설정
    @admin.action(description="선택 사용자 인증 승인 취소")
    def unapprove_users(self, request, queryset):
        updated = queryset.update(is_verified=False, verified_at=None)
        self.message_user(request, f"{updated}명의 사용자 승인을 취소했습니다.")

    # 저장 시 verified 상태에 따라 시간 자동 반영
    def save_model(self, request, obj, form, change):
        if change and "is_verified" in form.changed_data:
            obj.verified_at = timezone.now() if obj.is_verified else None
        super().save_model(request, obj, form, change)