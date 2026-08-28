"""鉴权相关视图。

健康检查 / 登录 / 登出 / 用户信息
"""

from __future__ import annotations

import time

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from ..models import Menu, User
from .common import (
    APIView,
    _get_current_user,
    _get_token_from_request,
    _issue_token,
    _log_operation,
    _TOKENS,
    fail,
    ok,
    require_auth,
)


class HealthCheckView(APIView):
    def get(self, request):
        return Response(ok({"status": "ok", "time": timezone.now().isoformat()}))


class LoginView(APIView):
    def post(self, request):
        start = time.perf_counter()
        username = (request.data or {}).get("username") or (request.data or {}).get("userName")
        password = (request.data or {}).get("password")
        if not username or not password:
            return Response(fail("账号和密码不能为空"))
        user = User.objects.filter(username=username, is_deleted=False).first()
        if not user:
            return Response(fail("账号或密码错误"), status=status.HTTP_200_OK)
        if user.status != "1":
            return Response(fail("账号已被停用"))
        if not user.check_password(password):
            _log_operation(
                request,
                "auth",
                f"{username} 登录失败",
                op_type="8",
                status="0",
                cost=int((time.perf_counter() - start) * 1000),
                error_msg="密码错误",
            )
            return Response(fail("账号或密码错误"))
        token, refresh = _issue_token(user)
        user.login_ip = _get_token_from_request and request.META.get("REMOTE_ADDR", "")
        # 真实登录 IP 走标准 get_client_ip（common 中未导出时在此兜底）
        from .common import get_client_ip

        user.login_ip = get_client_ip(request)
        user.login_at = timezone.now()
        user.save(update_fields=["login_ip", "login_at"])
        _log_operation(
            request,
            "auth",
            f"{username} 登录成功",
            op_type="8",
            cost=int((time.perf_counter() - start) * 1000),
        )
        return Response(ok({"token": token, "refreshToken": refresh}))


class LogoutView(APIView):
    def post(self, request):
        token = _get_token_from_request(request)
        if token:
            entry = _TOKENS.pop(token, None)
            if entry and entry.get("refresh"):
                _TOKENS.pop(entry["refresh"], None)
        return Response(ok(True, msg="登出成功"))


class UserInfoView(APIView):
    @require_auth
    def get(self, request):
        u: User = request.sys_user
        role_codes = list(u.roles.values_list("code", flat=True))
        menu_perms = list(
            Menu.objects.filter(
                roles__in=u.roles.all(),
                is_deleted=False,
                status="1",
                permission__gt="",
            ).values_list("permission", flat=True)
        )
        # 超管自动持有所有按钮权限
        if "R_SUPER" in role_codes:
            menu_perms = list(
                Menu.objects.filter(
                    is_deleted=False, status="1", permission__gt=""
                ).values_list("permission", flat=True)
            )
        data = {
            "userId": str(u.id),
            "userName": u.username,
            "nickname": u.nickname,
            "avatar": u.avatar,
            "email": u.email,
            "phone": u.phone,
            "dept": {
                "id": u.department_id,
                "name": u.department.name if u.department else "",
                "code": u.department.code if u.department else "",
            },
            "roles": role_codes,
            "buttons": list(dict.fromkeys(menu_perms)),
        }
        return Response(ok(data))
