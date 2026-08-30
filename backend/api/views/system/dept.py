"""部门管理 ViewSet。"""

from __future__ import annotations

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Department
from ...serializers import DepartmentFlatSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, crud_schema_view, ok


@extend_schema_view(**crud_schema_view("部门", "系统管理"))
class DepartmentViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = Department
    serializer_class = DepartmentFlatSerializer
    list_serializer_class = DepartmentFlatSerializer
    module_name = "部门管理"
    filter_map = {"name": "name__icontains", "status": "status", "code": "code"}

    @extend_schema(
        responses={200: OpenApiResponse(description="返回部门树数组，节点含 children 子列表")},
        summary="获取部门树",
        description="返回全量部门按 parentId 组装成的树形结构，供部门管理与用户表单选择部门使用。",
        tags=["系统管理"],
    )
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

    @extend_schema(
        responses={200: OpenApiResponse(description="返回 [{id, name, code, parent_id}]，按 sort_order 排序")},
        summary="获取部门下拉选项",
        description="返回部门精简列表（按 sort_order 排序），供用户管理等表单下拉选择部门使用。",
        tags=["系统管理"],
    )
    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        rows = list(
            self._base_qs().order_by("sort_order", "id").values("id", "name", "code", "parent_id")
        )
        return Response(ok(rows))
