"""角色管理 ViewSet。"""

from __future__ import annotations

from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Role
from ...serializers import RoleSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, _log_operation, bump_routes_version, ok


class RoleViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = Role
    serializer_class = RoleSerializer
    module_name = "角色管理"
    filter_map = {"name": "name__icontains", "code": "code__icontains", "status": "status"}

    def _after_mutation(self, instance=None):
        # 角色新增/修改(含 menuIds)/删除都会影响用户动态路由，全局失效
        bump_routes_version()

    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        rows = list(self._base_qs().filter(status="1").values("id", "name", "code"))
        return Response(ok(rows))

    @action(detail=True, methods=["post"], url_path="assign-menus")
    def assign_menus(self, request, pk=None):
        role = self._base_qs().get(pk=pk)
        data = request.data or {}
        menu_ids = data.get("menuIds") or []
        role.menus.set(menu_ids)
        # 数据权限随权限分配面板一并提交（可选）
        data_scope = data.get("dataScope")
        if data_scope:
            role.data_scope = data_scope
            role.save(update_fields=["data_scope"])
        bump_routes_version()
        _log_operation(request, self.module_name, f"分配权限: {role.name}", op_type="5")
        return Response(ok(True))
