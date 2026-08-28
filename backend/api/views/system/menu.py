"""菜单管理 ViewSet。"""

from __future__ import annotations

from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Menu
from ...serializers import MenuFlatSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, bump_routes_version, ok


class MenuViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = Menu
    serializer_class = MenuFlatSerializer
    list_serializer_class = MenuFlatSerializer
    module_name = "菜单管理"
    filter_map = {"name": "name__icontains", "status": "status", "menuType": "menu_type"}

    def _after_mutation(self, instance=None):
        bump_routes_version()

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        qs = self._apply_query_filters(Menu.objects.filter(is_deleted=False), request)
        all_items = MenuFlatSerializer(qs, many=True).data
        for d in all_items:
            d["children"] = []
        by_id = {d["id"]: d for d in all_items}
        for d in all_items:
            if d["parentId"] and d["parentId"] in by_id:
                by_id[d["parentId"]]["children"].append(d)
        return Response(ok([d for d in all_items if not d["parentId"]]))

    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        rows = list(
            self._base_qs()
            .filter(status="1")
            .values("id", "name", "title", "parent_id", "menu_type")
        )
        return Response(ok(rows))
