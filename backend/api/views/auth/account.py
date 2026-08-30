"""鉴权相关视图。

健康检查 / 登录 / 登出 / 用户信息
"""

from __future__ import annotations

import random
import time
import uuid

from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response

from ...models import Menu, User
from ...serializers.schemas import LoginRequestSerializer
from ..common import (
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

# ============ 图形验证码 ============
CAPTCHA_TTL = 300  # 验证码有效期（秒）
_CAPTCHA_COLORS = ["#6366f1", "#8b5cf6", "#ec4899", "#0ea5e9", "#10b981", "#f59e0b"]
_CAPTCHAS: dict[str, tuple[str, float]] = {}  # key -> (计算结果, 过期时间戳)


def _gen_captcha_svg() -> tuple[str, str]:
    """生成 20 以内加减法验证码（结果一定为正数）及对应 SVG，返回 (计算结果, SVG 字符串)。"""
    a = random.randint(1, 19)
    if a > 1 and random.random() < 0.5:
        # 减法：b < a，保证结果为正数
        b = random.randint(1, a - 1)
        expr, answer = f"{a}-{b}", a - b
    else:
        # 加法：两数之和不超过 20
        b = random.randint(1, 20 - a)
        expr, answer = f"{a}+{b}", a + b
    w, h = 120, 40
    grad = random.randint(1000, 9999)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        # 柔和的靛蓝渐变圆角背景
        f'<defs><linearGradient id="g{grad}" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#eef2ff"/><stop offset="1" stop-color="#e0e7ff"/>'
        "</linearGradient></defs>",
        f'<rect width="{w}" height="{h}" rx="6" fill="url(#g{grad})"/>',
    ]
    # 干扰曲线
    for _ in range(3):
        x1, y1 = random.randint(0, w // 3), random.randint(4, h - 4)
        x2, y2 = random.randint(w // 3, 2 * w // 3), random.randint(4, h - 4)
        x3, y3 = random.randint(2 * w // 3, w), random.randint(4, h - 4)
        parts.append(
            f'<path d="M{x1},{y1} Q{x2},{y2} {x3},{y3}" fill="none" '
            f'stroke="{random.choice(_CAPTCHA_COLORS)}" stroke-width="1.2" opacity="0.3"/>'
        )
    # 表达式字符：如 "12+7=?"，随机颜色、字号、轻微旋转
    x = 12
    for ch in f"{expr}=?":
        size = random.randint(20, 24)
        y = h / 2 + size / 3
        rot = random.randint(-12, 12)
        parts.append(
            f'<text x="{x}" y="{y:.1f}" font-family="Verdana,Arial,sans-serif" font-size="{size}" '
            f'font-weight="700" fill="{random.choice(_CAPTCHA_COLORS)}" fill-opacity="0.85" '
            f'transform="rotate({rot} {x} {y:.1f})">{ch}</text>'
        )
        x += 17
    # 噪点
    for _ in range(10):
        parts.append(
            f'<circle cx="{random.randint(3, w - 3)}" cy="{random.randint(3, h - 3)}" '
            f'r="1" fill="{random.choice(_CAPTCHA_COLORS)}" opacity="0.35"/>'
        )
    parts.append("</svg>")
    return str(answer), "".join(parts)


class CaptchaView(APIView):
    """获取图形验证码，返回 {key, svg}，登录时需回传。"""

    @extend_schema(
        responses={200: OpenApiResponse(description="返回 {key, svg}")},
        summary="获取图形验证码",
    )
    def get(self, request):
        now = time.time()
        # 顺带清理过期验证码
        for k in [k for k, (_, exp) in _CAPTCHAS.items() if exp < now]:
            _CAPTCHAS.pop(k, None)
        code, svg = _gen_captcha_svg()
        key = uuid.uuid4().hex
        _CAPTCHAS[key] = (code, now + CAPTCHA_TTL)
        return Response(ok({"key": key, "svg": svg}))


class HealthCheckView(APIView):
    def get(self, request):
        return Response(ok({"status": "ok", "time": timezone.now().isoformat()}))


class LoginView(APIView):
    @extend_schema(
        request=LoginRequestSerializer,
        responses={200: OpenApiResponse(description="返回 {token, refreshToken}")},
        summary="登录获取 Token",
    )
    def post(self, request):
        start = time.perf_counter()
        username = (request.data or {}).get("username") or (request.data or {}).get("userName")
        password = (request.data or {}).get("password")
        if not username or not password:
            return Response(fail("账号和密码不能为空"))
        # 校验图形验证码（一次性使用，按数值比较计算结果）
        captcha_key = str((request.data or {}).get("captchaKey") or "")
        captcha_code = str((request.data or {}).get("captchaCode") or "").strip()
        entry = _CAPTCHAS.pop(captcha_key, None)
        try:
            captcha_ok = bool(entry) and entry[1] >= time.time() and int(entry[0]) == int(captcha_code)
        except ValueError:
            captcha_ok = False
        if not captcha_ok:
            return Response(fail("验证码错误或已过期"))
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
        from ..common import get_client_ip

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
