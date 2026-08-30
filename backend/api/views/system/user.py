"""用户管理 ViewSet。"""

from __future__ import annotations

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import User
from ...serializers import UserSerializer
from ..common import (
    AuthenticatedViewSet,
    _CRUDMixin,
    _log_operation,
    crud_schema_view,
    fail,
    invalidate_user_routes,
    ok,
)


@extend_schema_view(**crud_schema_view("用户", "系统管理"))
class UserViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = User
    serializer_class = UserSerializer
    module_name = "用户管理"
    filter_map = {
        "username": "username__icontains",
        "nickname": "nickname__icontains",
        "phone": "phone__icontains",
        "status": "status",
        "deptId": "department_id",
        "department": "department_id",
    }

    def _after_mutation(self, instance=None):
        # 用户角色可能被修改，按用户失效其动态路由缓存
        if instance is not None:
            invalidate_user_routes(instance.id)

    @extend_schema(
        request=None,
        responses={200: OpenApiResponse(description="data 固定为 true")},
        summary="重置用户密码",
        description="按用户 ID 重置登录密码；请求体可不传，默认重置为 123456。",
        tags=["系统管理"],
    )
    @action(detail=True, methods=["post"], url_path="reset-pwd")
    def reset_pwd(self, request, pk=None):
        u = self._base_qs().get(pk=pk)
        raw = (request.data or {}).get("password") or "123456"
        u.set_password(raw)
        u.save(update_fields=["password"])
        _log_operation(request, self.module_name, f"重置密码: {u.username}", op_type="3")
        return Response(ok(True))

    @extend_schema(
        responses={200: OpenApiResponse(description="data 固定为 true；状态值非法时返回错误")},
        summary="修改用户状态",
        description="启用（1）/ 停用（0）指定用户账号，请求体传 { status: '0' | '1' }。停用后该用户无法登录。",
        tags=["系统管理"],
    )
    @action(detail=True, methods=["post"], url_path="change-status")
    def change_status(self, request, pk=None):
        u = self._base_qs().get(pk=pk)
        s = (request.data or {}).get("status")
        if s not in ("0", "1"):
            return Response(fail("状态值非法"))
        u.status = s
        u.save(update_fields=["status"])
        _log_operation(request, self.module_name, f"修改状态: {u.username} -> {s}", op_type="3")
        return Response(ok(True))
