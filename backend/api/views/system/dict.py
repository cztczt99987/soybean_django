"""字典管理 ViewSet。

字典类型 DictType + 字典数据 DictData 放在同一文件内，对应前端双 Tab。
"""

from __future__ import annotations

from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import DictData, DictType
from ...serializers import DictDataSerializer, DictTypeSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, fail, ok


class DictTypeViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = DictType
    serializer_class = DictTypeSerializer
    module_name = "字典管理"
    filter_map = {"name": "name__icontains", "code": "code__icontains", "status": "status"}

    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        rows = list(self._base_qs().filter(status="1").values("id", "name", "code"))
        return Response(ok(rows))

    @action(detail=True, methods=["get"], url_path="items")
    def items(self, request, pk=None):
        dtype = self._base_qs().get(pk=pk)
        rows = DictData.objects.filter(dict_type=dtype, is_deleted=False)
        return Response(ok(DictDataSerializer(rows, many=True).data))


class DictDataViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = DictData
    serializer_class = DictDataSerializer
    module_name = "字典明细"
    filter_map = {"label": "label__icontains", "status": "status", "dictCode": "dict_type__code"}

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
