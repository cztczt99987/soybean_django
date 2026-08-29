"""DRF 自定义异常处理：保证所有异常返回体都是 {code,msg,data}。"""

from __future__ import annotations

from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied, ErrorDetail
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status as http_status

from .views import AUTH_CODE, ERROR_CODE, fail


def _join_msg(detail) -> str:
    if detail is None:
        return ""
    if isinstance(detail, (list, tuple)):
        return "; ".join(_join_msg(x) for x in detail)
    if isinstance(detail, dict):
        parts = []
        for k, v in detail.items():
            if isinstance(v, list):
                for i in v:
                    parts.append(f"{k}: {_join_msg(i)}")
            else:
                parts.append(f"{k}: {_join_msg(v)}")
        return "; ".join(parts)
    if isinstance(detail, ErrorDetail):
        return str(detail)
    return str(detail)


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        # 5xx 类异常
        msg = str(exc) or "服务端异常"
        return Response(
            fail(msg, code=ERROR_CODE),
            status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    detail = getattr(response, "data", None)
    msg = _join_msg(detail) or "请求失败"
    code = ERROR_CODE
    http_code = response.status_code
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed, PermissionDenied)):
        # 未配置 DRF 认证类时 401 会被降级为 403, 这里强制回 401 (前端依赖其判断登录态)
        code = AUTH_CODE
        http_code = http_status.HTTP_401_UNAUTHORIZED
    return Response(fail(msg, code=code), status=http_code)
