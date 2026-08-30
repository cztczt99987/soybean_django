"""任务执行日志视图。"""

from __future__ import annotations

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import TaskExecutionLog
from ...serializers import TaskExecutionLogSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, _log_operation, crud_schema_view, ok


@extend_schema_view(**crud_schema_view("任务执行日志", "任务管理"))
class TaskExecutionLogViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = TaskExecutionLog
    serializer_class = TaskExecutionLogSerializer
    module_name = "任务执行日志"
    filter_map = {"job": "job_id", "status": "status", "job_name": "job_name__icontains"}

    @extend_schema(
        responses={200: OpenApiResponse(description="返回 {deleted: 删除条数}")},
        summary="清空执行日志",
        description="物理删除全部任务执行日志（不可恢复），操作会记录操作日志。",
        tags=["任务管理"],
    )
    @action(detail=False, methods=["post"], url_path="clear")
    def clear(self, request):
        deleted, _ = TaskExecutionLog.objects.all().delete()
        _log_operation(request, "任务执行日志", f"清空执行日志 {deleted} 条", op_type="4")
        return Response(ok({"deleted": deleted}))
