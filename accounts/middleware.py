from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class VerificationRequiredMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        user = request.user

        if user.is_staff or user.is_superuser:
            return None

        if not user.is_authenticated:
            return None

        if user.is_verified:
            return None

        resolver = request.resolver_match
        if resolver is None:
            return None

        namespace = resolver.namespace
        url_name = resolver.url_name

        allowed = {
            ("accounts", "login"),
            ("accounts", "signup"),
            ("accounts", "logout"),
            ("accounts", "verification"),
            ("accounts", "departments_api"),
            ("home", "home"),
        }

        if (namespace, url_name) not in allowed:
            return redirect("accounts:verification")

        return None
