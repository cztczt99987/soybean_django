"""操作日志 ViewSet。

只读 + 删除 / 批量删除 / 清理（N 天前）。
"""

from __future__ import annotations

from datetime import timedelta

from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import OperationLog
from ...serializers import OperationLogSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, crud_schema_view, ok


@extend_schema_view(**crud_schema_view("操作日志", "系统管理"))
class OperationLogViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = OperationLog
    serializer_class = OperationLogSerializer
    module_name = "操作日志"
    http_method_names = ["get", "delete", "head", "options"]
    filter_map = {
        "username": "username__icontains",
        "module": "module__icontains",
        "description": "description__icontains",
        "operationType": "operation_type",
        "status": "status",
    }

    @extend_schema(
        responses={200: OpenApiResponse(description="返回 {deleted: 删除条数}")},
        summary="清理历史日志",
        description="物理删除指定天数之前的操作日志，请求体传 { days: 30 }（默认 30 天）。",
        tags=["系统管理"],
    )
    @action(detail=False, methods=["post"], url_path="clean")
    def clean(self, request):
        days = int((request.data or {}).get("days") or 30)
        threshold = timezone.now() - timedelta(days=days)
        n, _ = OperationLog.objects.filter(operated_at__lt=threshold).delete()
        return Response(ok({"deleted": n}))
