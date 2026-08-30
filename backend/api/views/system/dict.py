"""字典管理 ViewSet。

字典类型 DictType + 字典数据 DictData 放在同一文件内，对应前端双 Tab。
"""

from __future__ import annotations

from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import DictData, DictType
from ...serializers import DictDataSerializer, DictTypeSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, crud_schema_view, fail, ok


@extend_schema_view(**crud_schema_view("字典类型", "系统管理"))
class DictTypeViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = DictType
    serializer_class = DictTypeSerializer
    module_name = "字典管理"
    filter_map = {"name": "name__icontains", "code": "code__icontains", "status": "status"}

    @extend_schema(
        responses={200: OpenApiResponse(description="返回 [{id, name, code}]，仅含启用状态的字典类型")},
        summary="获取字典类型下拉选项",
        description="返回全部启用状态字典类型的精简列表，供字典数据关联、表单下拉等场景使用。",
        tags=["系统管理"],
    )
    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        rows = list(self._base_qs().filter(status="1").values("id", "name", "code"))
        return Response(ok(rows))

    @extend_schema(
        responses={200: OpenApiResponse(description="返回该字典类型下的字典数据数组")},
        summary="查询字典类型下的字典数据",
        description="按字典类型 ID 查询其下全部字典数据项（不限启用状态），供字典管理页面明细 Tab 使用。",
        tags=["系统管理"],
    )
    @action(detail=True, methods=["get"], url_path="items")
    def items(self, request, pk=None):
        dtype = self._base_qs().get(pk=pk)
        rows = DictData.objects.filter(dict_type=dtype, is_deleted=False)
        return Response(ok(DictDataSerializer(rows, many=True).data))


@extend_schema_view(**crud_schema_view("字典数据", "系统管理"))
class DictDataViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = DictData
    serializer_class = DictDataSerializer
    module_name = "字典明细"
    filter_map = {"label": "label__icontains", "status": "status", "dictCode": "dict_type__code"}

    @extend_schema(
        parameters=[OpenApiParameter("code", str, OpenApiParameter.QUERY, description="字典类型编码，如 sys_yes_no")],
        responses={200: OpenApiResponse(description="返回启用状态的字典数据数组；类型不存在时返回空数组")},
        summary="按类型编码查询字典数据",
        description="按字典类型编码（code）查询其启用状态的字典数据项，按 sort_order 排序，供前端表单渲染下拉/单选使用。",
        tags=["系统管理"],
    )
    @action(detail=False, methods=["get"], url_path="by-code")
    def by_code(self, request):
        code = (request.query_params.get("code") or "").strip()
        if not code:
            return Response(fail("请传入字典编码 code"))
        try:
            dtype = DictType.objects.get(code=code, is_deleted=False)
        except DictType.DoesNotExist:
            return Response(ok([]))
        rows = DictData.objects.filter(
            dict_type=dtype, is_deleted=False, status="1"
        ).order_by("sort_order", "id")
        return Response(ok(DictDataSerializer(rows, many=True).data))
