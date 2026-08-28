"""部门管理 ViewSet。"""

from __future__ import annotations

from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Department
from ...serializers import DepartmentFlatSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, ok


class DepartmentViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = Department
    serializer_class = DepartmentFlatSerializer
    list_serializer_class = DepartmentFlatSerializer
    module_name = "部门管理"
    filter_map = {"name": "name__icontains", "status": "status", "code": "code"}

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        qs = self._apply_query_filters(Department.objects.filter(is_deleted=False), request)
        all_items = DepartmentFlatSerializer(qs, many=True).data
        for d in all_items:
            d["children"] = []
        node_by_id = {d["id"]: d for d in all_items}
        for d in all_items:
            if d["parentId"] and d["parentId"] in node_by_id:
                node_by_id[d["parentId"]]["children"].append(d)
        trees = [d for d in all_items if not d["parentId"]]
        return Response(ok(trees))

    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        rows = list(
            self._base_qs().order_by("sort_order", "id").values("id", "name", "code", "parent_id")
        )
        return Response(ok(rows))
