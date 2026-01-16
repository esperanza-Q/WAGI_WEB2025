from django.contrib import admin
from .models import User, College, Department, Verification

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
    list_display = ("username", "display_name", "email", "is_verified", "department", "college", "grade")
    search_fields = ("username", "display_name", "email", "department__dept_name", "department__college__college_name", "grade")
    list_filter = ("is_verified", "department", "department__college", "grade",)
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
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated}명의 사용자를 승인했습니다.")

    # unapprove_users: 선택한 사용자들의 is_verified를 False로 설정하고 verified_at을 None으로 설정
    @admin.action(description="선택 사용자 인증 승인 취소")
    def unapprove_users(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"{updated}명의 사용자 승인을 취소했습니다.")

@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",               # User(학번) 연결
        "real_name",          # 성명
        "verification_document",
        "is_verified",
    )
    search_fields = (
        "real_name",
        "user__username",
    )
    list_filter = ("is_verified",)

    actions = ["is_verified_selected"]

    @admin.action(description="선택 인증요청 승인 + 유저 is_verified=True 처리")
    def is_verified_selected(self, request, queryset):
        count = 0
        for ver in queryset.select_related("user"):
            if ver.is_verified:
                continue
            ver.is_verified = True
            ver.save(update_fields=["is_verified"])
            if hasattr(ver.user, "is_verified") and not ver.user.is_verified:
                ver.user.is_verified = True
                ver.user.save(update_fields=["is_verified"])
                count += 1
            self.message_user(request, f"{count}명의 사용자를 인증 처리했습니다.")
    def save_model(self, request, obj, form, change):
            super().save_model(request, obj, form, change)
            if obj.is_verified and hasattr(obj.user, "is_verified") and not obj.user.is_verified:
                obj.user.is_verified = True
                obj.user.save(update_fields=["is_verified"])