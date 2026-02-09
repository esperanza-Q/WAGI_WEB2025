from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class VerificationRequiredMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        user = request.user

        resolver = request.resolver_match
        if resolver is None:
            return None

        namespace = resolver.namespace
        url_name = resolver.url_name

        # 🔓 로그인 안 해도 허용할 URL
        public_urls = {
            ("accounts", "login"),
            ("accounts", "signup"),
            ("home", "home"),
        }

        # 🔓 로그인은 했지만 인증 안 해도 허용할 URL
        verification_urls = {
            ("accounts", "logout"),
            ("accounts", "verification"),
            ("accounts", "departments_api"),
        }

        # ✅ 관리자 무조건 통과
        if user.is_staff or user.is_superuser:
            return None

        # ❌ 로그인 안 한 유저
        if not user.is_authenticated:
            if (namespace, url_name) in public_urls:
                return None
            return redirect("accounts:login")

        # ❌ 로그인 했지만 인증 안 한 유저
        if not getattr(user, "is_verified", False):
            if (namespace, url_name) in public_urls | verification_urls:
                return None
            return redirect("accounts:verification")

        # ✅ 인증된 유저
        return None