"""菜单管理 ViewSet。"""

from __future__ import annotations

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Menu
from ...serializers import MenuFlatSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, bump_routes_version, crud_schema_view, ok


@extend_schema_view(**crud_schema_view("菜单", "系统管理"))
class MenuViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = Menu
    serializer_class = MenuFlatSerializer
    list_serializer_class = MenuFlatSerializer
    module_name = "菜单管理"
    filter_map = {"name": "name__icontains", "status": "status", "menuType": "menu_type"}

    def _after_mutation(self, instance=None):
        bump_routes_version()

    @extend_schema(
        responses={200: OpenApiResponse(description="返回菜单树数组，节点含 children 子列表")},
        summary="获取菜单树",
        description="返回全量菜单按 parentId 组装成的树形结构（目录/菜单/按钮），供菜单管理与权限分配面板使用。",
        tags=["系统管理"],
    )
    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        qs = self._apply_query_filters(Menu.objects.filter(is_deleted=False), request).order_by("order", "id")
        all_items = MenuFlatSerializer(qs, many=True).data
        for d in all_items:
            d["children"] = []
        by_id = {d["id"]: d for d in all_items}
        for d in all_items:
            if d["parentId"] and d["parentId"] in by_id:
                by_id[d["parentId"]]["children"].append(d)
        return Response(ok([d for d in all_items if not d["parentId"]]))

    @extend_schema(
        responses={200: OpenApiResponse(description="返回 [{id, name, title, parent_id, menu_type}]，仅启用状态")},
        summary="获取菜单下拉选项",
        description="返回启用状态菜单的精简列表，供新建/编辑菜单时选择父级目录等场景使用。",
        tags=["系统管理"],
    )
    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        rows = list(
            self._base_qs()
            .filter(status="1")
            .values("id", "name", "title", "parent_id", "menu_type")
        )
        return Response(ok(rows))
